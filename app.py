from flask import Flask, render_template, jsonify, send_file, request
from threading import Thread
from pymavlink import mavutil
from datetime import datetime
import subprocess
import os
import time

app = Flask(__name__)

# ======= Config =======
STREAM_URL = "http://<Pi-IP>:8080/?action=stream"  # Put your actual Pi IP here
ARM_STATE_FILE = "armed_state.txt"
LOG_FILE = "camera_logs.txt"

# Store latest telemetry
telemetry_data = {
    'depth': 0.0,
    'velocity': 0.0,
    'heading': 0.0
}

# ======= MAVLink listener thread =======
def mavlink_listener():
    mav = mavutil.mavlink_connection('udpin:192.168.2.1:14550')
    mav.wait_heartbeat()
    print(f"MAVLink heartbeat from sysid {mav.target_system} compid {mav.target_component}")

    while True:
        msg = mav.recv_match(blocking=True, timeout=1)
        if not msg:
            continue

        msg_type = msg.get_type()

        if msg_type == "VFR_HUD":
            telemetry_data['velocity'] = msg.groundspeed
            telemetry_data['heading'] = msg.heading
        elif msg_type in ["SCALED_PRESSURE2", "SCALED_PRESSURE"]:
            telemetry_data['depth'] = msg.press_abs

        time.sleep(0.05)

# ======= Flask routes =======
@app.route('/')
def index():
    return render_template('index.html', stream_url=STREAM_URL)

@app.route('/telemetry')
def telemetry():
    return jsonify(telemetry_data)

@app.route('/api/arm', methods=['GET'])
def arm_toggle():
    state = request.args.get("state", "false").lower() == "true"
    with open(ARM_STATE_FILE, "w") as f:
        f.write("ARMED" if state else "DISARMED")
    log_action(f"Arm state changed to {'ARMED' if state else 'DISARMED'}")
    return jsonify({"status": "ok", "armed": state})

@app.route('/api/snapshot')
def snapshot():
    filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    # Capture frame using ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-i", STREAM_URL, "-frames:v", "1", filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(filename):
        log_action("Snapshot captured")
        return send_file(filename, mimetype="image/jpeg", as_attachment=True)
    else:
        return jsonify({"error": "snapshot failed"}), 500

@app.route('/api/logs')
def logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            content = f.read()
    else:
        content = "No logs available."
    return content, 200, {"Content-Type": "text/plain"}

# ======= Helpers =======
def log_action(text):
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now()} - {text}\n")

if __name__ == "__main__":
    Thread(target=mavlink_listener, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)

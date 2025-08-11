from flask import Flask, render_template, jsonify
from threading import Thread
from pymavlink import mavutil
import time

app = Flask(__name__)

# Store latest telemetry data
telemetry_data = {
    'depth': 0.0,
    'velocity': 0.0,
    'heading': 0.0
}

# ====== MAVLink listener thread ======
def mavlink_listener():
    # Change connection string if your setup is different
    mav = mavutil.mavlink_connection('udpin:192.168.2.2:14550')
    mav.wait_heartbeat()
    print("MAVLink heartbeat received from system (sysid %u compid %u)" % (mav.target_system, mav.target_component))

    while True:
        msg = mav.recv_match(blocking=True, timeout=1)
        if not msg:
            continue
        msg_type = msg.get_type()

        # Example fields from common MAVLink messages
        if msg_type == "VFR_HUD":
            telemetry_data['velocity'] = msg.groundspeed  # m/s
            telemetry_data['heading'] = msg.heading       # degrees
        elif msg_type == "SCALED_PRESSURE2":  
            # Convert pressure to approximate depth if desired
            telemetry_data['depth'] = msg.press_abs  # raw pressure
        elif msg_type == "SCALED_PRESSURE":
            telemetry_data['depth'] = msg.press_abs

        time.sleep(0.05)

# ====== Flask routes ======
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/telemetry')
def telemetry():
    return jsonify(telemetry_data)

if __name__ == "__main__":
    # Start MAVLink listener in background
    Thread(target=mavlink_listener, daemon=True).start()

    # Run Flask web server on all interfaces
    app.run(host="0.0.0.0", port=8000)

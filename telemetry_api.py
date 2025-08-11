from flask import Flask, jsonify
from threading import Thread
from pymavlink import mavutil
import time

app = Flask(__name__)

# Store latest telemetry here
telemetry_data = {
    'depth': 0.0,
    'velocity': 0.0,
    'heading': 0.0
}

def mavlink_listener():
    # Connect to Pixhawk via UDP (adjust port/interface as needed)
    mav = mavutil.mavlink_connection('udpin:192.168.2.2:14551')
    mav.wait_heartbeat()
    print("MAVLink: Heartbeat received.")

    while True:
        msg = mav.recv_match(type=['VFR_HUD', 'SCALED_PRESSURE', 'ATTITUDE'], blocking=True, timeout=2)
        if msg:
            typ = msg.get_type()
            if typ == 'VFR_HUD':
                telemetry_data['velocity'] = msg.groundspeed
                telemetry_data['heading'] = msg.heading
            elif typ == 'SCALED_PRESSURE':
                telemetry_data['depth'] = msg.press_abs  # Substitute this for depth proxy (requires conversion if desired)
        time.sleep(0.1)

@app.route('/telemetry')
def telemetry():
    return jsonify(telemetry_data)

if __name__ == '__main__':
    Thread(target=mavlink_listener, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)

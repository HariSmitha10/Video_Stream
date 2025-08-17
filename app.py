# app.py
from flask import Flask, render_template, jsonify, send_file, request
from modules.logger_config import setup_logging
from modules.mavlink_manager import MAVLinkManager
from modules.camera_manager import CameraManager
import logging

# --- Application Configuration ---
# IMPORTANT: Update these values for your setup
STREAM_URL = "http://<YOUR_PI_IP>:8080/?action=stream"
MAVLINK_CONNECTION_STRING = 'udpin:192.168.2.1:14550'
LOG_FILE_PATH = "auv_system.log"

# --- System Initialization ---
setup_logging()
app = Flask(__name__)
mav_manager = MAVLinkManager(MAVLINK_CONNECTION_STRING)
camera_manager = CameraManager(STREAM_URL)

# Start background services
mav_manager.start()

# --- Flask Routes (API Endpoints) ---

@app.route('/')
def index():
    """Serves the main web interface."""
    return render_template('index.html')

@app.route('/telemetry')
def telemetry_endpoint():
    """Provides the latest vehicle telemetry data as JSON."""
    return jsonify(mav_manager.get_telemetry())

@app.route('/api/arm', methods=['POST'])
def arm_vehicle_endpoint():
    """API endpoint to arm or disarm the vehicle."""
    try:
        should_arm = request.json.get('state', False)
        message = mav_manager.arm_disarm(should_arm)
        return jsonify({"status": "ok", "message": message})
    except Exception as e:
        logging.error(f"Arm/Disarm API Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/snapshot')
def snapshot_endpoint():
    """API endpoint to capture a snapshot and send it for download."""
    try:
        filepath, filename = camera_manager.take_snapshot()
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/logs')
def logs_endpoint():
    """Provides the full content of the log file."""
    try:
        with open(LOG_FILE_PATH, "r") as f:
            return f.read(), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except FileNotFoundError:
        return "Log file not found.", 404

if __name__ == "__main__":
    # Use debug=False for production-like environments
    app.run(host="0.0.0.0", port=8000, debug=False)

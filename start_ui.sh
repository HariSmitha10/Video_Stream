#!/bin/bash
# Simple script to start combined AUV UI and Telemetry on laptop

# Change directory to your project folder (adjust if needed)
cd ~/Video_Stream || { echo "UI folder not found!"; exit 1; }

# Stop any running Python servers (combined Flask app)
pkill -f app.py

# Start the combined Flask app (serves UI and telemetry API together)
echo "Starting combined UI + telemetry backend..."
python3 app.py &
APP_PID=$!

# Wait until app initializes
sleep 1

# Get this machine's IP
MYIP=$(hostname -I | awk '{print $1}')

echo "---------------------------------------------------"
echo "✅ AUV UI and Telemetry API are running together!"
echo "Open your browser at:   http://localhost:8000"
echo "   or from another PC:  http://$MYIP:8000"
echo
echo "Raspberry Pi MJPEG stream still at:"
echo "   http://<Pi-IP>:8090/?action=stream"
echo "---------------------------------------------------"
echo "Press Ctrl+C to stop."

# Wait on the app process
wait $APP_PID

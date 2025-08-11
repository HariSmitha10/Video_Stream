#!/bin/bash
# Simple script to start AUV UI and Telemetry on laptop

# Change directory to your project folder (adjust if needed)
cd ~/Video_Stream || { echo "UI folder not found!"; exit 1; }

# Stop any running Python servers (HTTP UI or telemetry)
pkill -f server.py
pkill -f telemetry_api.py

# Start telemetry API in background
echo "Starting telemetry API backend..."
python3 telemetry_api.py &
TELEMETRY_PID=$!

# Wait until telemetry API initializes
sleep 1

# Start the UI HTTP server
echo "Starting UI server..."
python3 server.py &
UI_PID=$!

# Give info to the user
sleep 1
MYIP=$(hostname -I | awk '{print $1}')
echo "---------------------------------------------------"
echo "AUV UI is running!"
echo "Open your browser at:   http://localhost:8090"
echo "   or from another PC:  http://$MYIP:8090"
echo
echo "Telemetry API:       http://localhost:5000/telemetry"
echo "   or from another PC:  http://$MYIP:5000/telemetry"
echo
echo "Raspberry Pi MJPEG stream is still at:"
echo "   http://<Pi-IP>:8090/?action=stream"
echo "---------------------------------------------------"
echo "Press Ctrl+C to stop."

# Wait on both processes
wait $UI_PID $TELEMETRY_PID

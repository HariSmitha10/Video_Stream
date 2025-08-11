#!/bin/bash
# Simple script to start AUV UI and Telemetry on laptop

# Change directory to your project folder (adjust path)
cd ~/Video_Stream || { echo "UI folder not found!"; exit 1; }

# Stop any running Python servers (HTTP UI or telemetry)
pkill -f server.py
pkill -f telemetry_api.py

# Start telemetry API in background if needed
echo "Starting telemetry API backend..."
python3 telemetry_api.py &

# Wait 1 second to make sure telemetry API starts
sleep 1

# Start the UI HTTP server
echo "Starting UI server..."
python3 server.py &

# Give info to the user
sleep 1
echo "---------------------------------------------------"
echo "AUV UI is running!"
echo "Open your browser at: http://localhost:8090"
echo "Telemetry API is at:  http://localhost:5000/telemetry"
echo "Press Ctrl+C to stop."
echo "---------------------------------------------------"

# Keep script running (so closing terminal will stop servers)
wait

# /modules/camera_manager.py
import os
import subprocess
from datetime import datetime
import logging

class CameraManager:
    """Manages camera operations like taking snapshots."""

    def __init__(self, stream_url, snapshot_dir="snapshots"):
        self.stream_url = stream_url
        self.snapshot_dir = snapshot_dir
        os.makedirs(self.snapshot_dir, exist_ok=True)
        logging.info(f"Snapshots will be saved to '{self.snapshot_dir}' directory.")

    def take_snapshot(self):
        """Captures a snapshot from the stream and returns its file path and name."""
        filename = f"snapshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        filepath = os.path.join(self.snapshot_dir, filename)
        try:
            # Use ffmpeg to efficiently grab a single frame from the live stream
            subprocess.run(
                ["ffmpeg", "-y", "-i", self.stream_url, "-frames:v", "1", filepath],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            logging.info(f"Snapshot successfully saved: {filepath}")
            return filepath, filename
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_msg = f"Snapshot failed. Please ensure ffmpeg is installed and the stream URL is correct. Error: {e}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

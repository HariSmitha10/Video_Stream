# /modules/mavlink_manager.py
import logging
from pymavlink import mavutil
import time
from threading import Thread

class MAVLinkManager:
    """Handles all MAVLink communication in a separate thread."""

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.telemetry = {
            'depth': 0.0,
            'velocity': 0.0,
            'heading': 0.0,
            'armed': False
        }
        self.is_connected = False
        self._listener_thread = Thread(target=self._mavlink_listener, daemon=True)

    def start(self):
        """Starts the MAVLink listener thread."""
        self._listener_thread.start()
        logging.info("MAVLinkManager background thread started.")

    def _mavlink_listener(self):
        """The main loop for connecting and listening for MAVLink messages."""
        while True:
            try:
                if self.connection is None:
                    logging.info(f"Attempting to connect to MAVLink on {self.connection_string}...")
                    self.connection = mavutil.mavlink_connection(self.connection_string)
                    self.connection.wait_heartbeat()
                    self.is_connected = True
                    logging.info(f"MAVLink connection established (SysID: {self.connection.target_system})")

                msg = self.connection.recv_match(blocking=True, timeout=5)
                if not msg:
                    continue

                msg_type = msg.get_type()
                if msg_type == "HEARTBEAT":
                    self.telemetry['armed'] = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                elif msg_type == "VFR_HUD":
                    self.telemetry['velocity'] = msg.groundspeed
                    self.telemetry['heading'] = msg.heading
                elif msg_type in ["SCALED_PRESSURE2", "SCALED_PRESSURE"]:
                    self.telemetry['depth'] = msg.press_abs

            except Exception as e:
                logging.error(f"MAVLink connection error: {e}")
                self.is_connected = False
                self.connection = None
                time.sleep(5)  # Wait before retrying

    def arm_disarm(self, arm_state: bool):
        """Sends an Arm or Disarm command to the vehicle."""
        if not self.is_connected:
            raise ConnectionError("Cannot send command: MAVLink is not connected.")

        action_str = "ARM" if arm_state else "DISARM"
        logging.info(f"Sending {action_str} command to vehicle...")
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # Confirmation
            1.0 if arm_state else 0.0,
            0, 0, 0, 0, 0, 0
        )
        # For critical operations, you would wait for a COMMAND_ACK here.
        return f"{action_str} command sent successfully."

    def get_telemetry(self):
        """Returns the latest telemetry data."""
        return self.telemetry

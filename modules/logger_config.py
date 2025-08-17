# /modules/logger_config.py
import logging

def setup_logging():
    """Configures the root logger to output to a file and the console."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] - %(message)s',
        handlers=[
            logging.FileHandler("auv_system.log"),
            logging.StreamHandler()  # Also print logs to the console
        ]
    )
    logging.info("AUV GCS logging configured.")

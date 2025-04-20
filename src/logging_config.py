import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Get the directory of the current script and define the log directory relative to it
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Logs")

# Ensure the directory exists
os.makedirs(log_dir, exist_ok=True)

# Generate a log filename with current date and time
current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"TCCL_process_{current_time_str}.log"
log_file = os.path.join(log_dir, log_filename)

# Create a logger
logger = logging.getLogger("ToolChipLogger")
logger.setLevel(logging.INFO)

# Create rotating file handler
log_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
log_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

# Clear previous handlers if this gets reloaded
if logger.hasHandlers():
    logger.handlers.clear()

# Add handlers
logger.addHandler(log_handler)

# Optional console logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

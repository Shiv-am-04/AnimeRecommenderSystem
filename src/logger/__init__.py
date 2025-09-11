import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

LOG = 'logs'
MAX_LOG_SIZE = 5 * 1024 * 1024
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
BACKUP_COUNT = 3

# Get project root (directory containing this script's parent directories)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_path = os.path.join(project_root, LOG)
os.makedirs(log_path, exist_ok=True)
log_file_path = os.path.join(log_path, LOG_FILE)


def configure_logger():
    # custom logger
    logger = logging.getLogger()
    logger.setLevel('DEBUG')

    formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")

    # filehandler
    handler = RotatingFileHandler(log_file_path, backupCount=BACKUP_COUNT, maxBytes=MAX_LOG_SIZE)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    # console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)

    # adding handlers to logger
    logger.addHandler(handler)
    logger.addHandler(console)


configure_logger()
import logging
import os
from logging.handlers import RotatingFileHandler
from utils.constants import LOG_FORMAT, ERROR_LOG, OTHER_LOG, LOG_DIR

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Constants for log file paths
OPERATION_LOG_FILE = os.path.join(LOG_DIR, OTHER_LOG)
ERROR_LOG_FILE = os.path.join(LOG_DIR, ERROR_LOG)

# Configure operation logger
operation_logger = logging.getLogger('operation_logger')
operation_logger.setLevel(logging.INFO)
op_handler = RotatingFileHandler(OPERATION_LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
op_formatter = logging.Formatter(LOG_FORMAT)
op_handler.setFormatter(op_formatter)
operation_logger.addHandler(op_handler)

# Configure error logger
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
err_handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
err_formatter = logging.Formatter(LOG_FORMAT)
err_handler.setFormatter(err_formatter)
error_logger.addHandler(err_handler)

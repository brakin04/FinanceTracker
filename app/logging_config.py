import os
import logging
from .file_functions import search_file, edit_file, get_file_content
from flask import session, has_request_context


LOGGER_NAME = "FinanceLogger"
_bootstrap_logger = logging.getLogger(LOGGER_NAME)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class SessionIDFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.session_id = session.get('session_id', 'None')
        else:
            record.session_id = 'No-Context'
        return True


#-------------------------------
# Sets up the logger with file and console handlers
def setup_logger(log_filename: str, level=logging.INFO):
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("FinanceLogger")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    # remove existing handlers (CRITICAL)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Remove default logs 
    logging.getLogger('werkzeug').handlers = []
    log = logging.getLogger('werkzeug')
    log.setLevel(100)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - id:%(session_id)s',
        '%Y-%m-%dT%H:%M:%S'
    )

    file_handler = logging.FileHandler(os.path.join(log_dir, log_filename))
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SessionIDFilter())
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


#-------------------------------
# Used to get or set the saved log level in config.txt
def savedLevel(type: str | None = "GET", value: str | None = None):
    logger = logging.getLogger("FinanceLogger")
    logger.info(f"savedLevel in logging_config.py called with type: {type}, value: {value}")
    idx = -1
    level = None
    idx = search_file(file_name="config.txt", content="log-level:", starts_with=True)
    if idx != -1:
        level = get_file_content(file_name="config.txt", line_idx=idx).split(": ")[1].strip()
    # Recieve the log level
    if type == "GET":
        if not level:
            logger.warning("No log level found in config, defaulting to INFO")
            return logging.INFO  # Default log level
        logger.info(f"Log level set to {level} from config")
        if level == "DEBUG":
            return logging.DEBUG
        elif level == "INFO":
            return logging.INFO
        elif level == "WARNING":
            return logging.WARNING
        elif level == "ERROR":
            return logging.ERROR
        elif level == "CRITICAL":
            return logging.CRITICAL         
    else:
        # Set the log level
        logger.info(f"Updating log level to {value} in config")
        success = edit_file(file_name="config.txt", old_content="log-level:", new_content=f"log-level: {value}", starts_with=True)
        if not success:
            logger.error("Failed to update log level in config")
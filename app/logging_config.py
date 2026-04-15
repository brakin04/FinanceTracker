import os
import logging


LOGGER_NAME = "FinanceLogger"
_bootstrap_logger = logging.getLogger(LOGGER_NAME)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

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
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%Y-%m-%dT%H:%M:%S'
    )

    file_handler = logging.FileHandler(os.path.join(log_dir, log_filename))
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger



# Function to get or set the saved log level in config.txt
def savedLevel(type: str | None = "GET", value: str | None = None):
    logger = logging.getLogger("FinanceLogger")
    logger.info(f"savedLevel function in logging_config.py called with type: {type}, value: {value}")
    idx = -1
    level = None
    data = []
    with open("config.txt", 'r') as f:
        data = f.readlines()
        for line in data:
            idx += 1
            if line.startswith("log-level:"):
                level = line.split(": ")[1].strip()
                break
        f.close()
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
        logger.info(f"Setting log level to {value} in config")
        with open("config.txt", 'w') as f:
            if idx != -1:
                data[idx] = f"log-level: {value}\n"
            f.writelines(data)
            f.close()
        return
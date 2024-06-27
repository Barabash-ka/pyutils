import logging
import os

DEFAULT_LOG_DIR = 'logs'
DEFAULT_LOG_FILE = 'default.log'

def setup_logging(log_file_name=DEFAULT_LOG_FILE, log_level = logging.DEBUG):
    log_format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    log_handlers=[]
    log_handlers.append(logging.StreamHandler())
    if log_file_name:
        log_file = f"{DEFAULT_LOG_DIR}{os.sep}{log_file_name}"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        log_handlers.append(file_handler)
        
    logging.basicConfig(level=log_level,
                        format=log_format,
                        handlers=log_handlers)

    logger = logging.getLogger(__name__)

    logger.info(f"Logging setup with level={log_level}")
    logger.info(f"Reducing noise from exif._image")
    logging.getLogger('exif._image').setLevel(logging.ERROR)
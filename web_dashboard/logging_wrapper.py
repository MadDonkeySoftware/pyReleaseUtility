import os.path as path
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

# https://docs.python.org/2/library/logging.html#logrecord-attributes
DEFAULT_LOG_MAX_BYTES = 1024 * 1024
DEFAULT_LOG_MESSAGE_FORMAT = ('%(asctime)s - %(process)s - %(thread)s - '
                              '%(levelname)s - %(module)s - %(funcName)s - '
                              '%(lineno)s - %(message)s')
DEFAULT_LOG_FILE_COUNT = 3
DEFAULT_LOG_NAME = 'pyReleaseUtility'
DEFAULT_LOG_FILE_PATH = ''
INITIALIZED = False


def initialize(config, flask_app=None):
    global DEFAULT_LOG_NAME
    global INITIALIZED
    if INITIALIZED:
        return

    # Get the values from our config, if they exist
    logger_name = (
        DEFAULT_LOG_NAME if 'LOG_NAME' not in config
        else config['LOG_NAME'])
    log_file_path = (
        DEFAULT_LOG_FILE_PATH if 'LOG_FILE_PATH' not in config
        else config['LOG_FILE_PATH'])
    log_message_format = (
        DEFAULT_LOG_MESSAGE_FORMAT if 'LOG_MESSAGE_FORMAT' not in config
        else config['LOG_MESSAGE_FORMAT'])
    log_file_count = (
        DEFAULT_LOG_FILE_COUNT if 'LOG_FILE_COUNT' not in config
        else config['LOG_FILE_COUNT'])
    log_max_file_bytes = (
        DEFAULT_LOG_MAX_BYTES if 'LOG_MAX_FILE_BYTES' not in config
        else config['LOG_MAX_FILE_BYTES'])

    # Update the default log name
    DEFAULT_LOG_NAME = logger_name

    # Build application logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Build the logging formatter
    formatter = logging.Formatter(log_message_format)

    # Configure default rotating handler
    log_rotating_handler = RotatingFileHandler(
        filename=path.join(log_file_path, logger_name + '.log'),
        backupCount=log_file_count,
        maxBytes=log_max_file_bytes)
    log_rotating_handler.setLevel(logging.NOTSET)
    log_rotating_handler.setFormatter(formatter)
    _add_flask_logging_handler(flask_app, log_rotating_handler)

    # Configure error specific rotating handler
    err_rotating_handler = RotatingFileHandler(
        filename=path.join(log_file_path, logger_name + '.err.log'),
        backupCount=log_file_count,
        maxBytes=log_max_file_bytes)
    err_rotating_handler.setLevel(logging.ERROR)
    err_rotating_handler.setFormatter(formatter)
    _add_flask_logging_handler(flask_app, err_rotating_handler)

    INITIALIZED = True


def get_logger(name=None):
    """
    :rtype: Logger
    """
    return logging.getLogger(name or DEFAULT_LOG_NAME)


def _add_flask_logging_handler(app, handler):
    if app is not None:
        app.logger.addHandler(handler)

    logger = get_logger()
    logger.addHandler(handler)

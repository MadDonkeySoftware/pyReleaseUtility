import injector
import flask
import logging
import os

from injector import Module
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


class WebInitializer(Module):
    LOG_FORMAT = '%(asctime)s - %(process)d - %(levelname)s - ' \
                 '%(pathname)s - %(funcName)s - %(lineno)s - %(message)s'

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger('web_dashboard')

    def configure(self, binder):
        log_file_name = 'web_dashboard'
        self.app.config['LOG_FILE_NAME'] = log_file_name
        self.configure_logger(log_file_name)

        binder.bind(flask.Config, to=self.app.config, scope=injector.singleton)
        binder.bind(logging.Logger, to=self.logger, scope=injector.singleton)

    def configure_logger(self, log_file_name='unnamed'):
        logs_dir = os.path.join(self.app.config['LOGS_DIR'], 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        megabyte = 1024 * 1024
        log_size = megabyte * 50
        err_size = megabyte * 10

        formatter = logging.Formatter(self.LOG_FORMAT)

        log_file = os.path.join(logs_dir, log_file_name)
        log_roll_file_handler = RotatingFileHandler('{0}.log'.format(log_file),
                                                    maxBytes=log_size,
                                                    backupCount=5)
        err_roll_file_handler = RotatingFileHandler('{0}.err'.format(log_file),
                                                    maxBytes=err_size,
                                                    backupCount=5)
        console_handler = StreamHandler()

        log_roll_file_handler.setFormatter(formatter)
        log_roll_file_handler.setLevel(logging.DEBUG)

        err_roll_file_handler.setFormatter(formatter)
        err_roll_file_handler.setLevel(logging.INFO)

        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(log_roll_file_handler)
        self.logger.addHandler(err_roll_file_handler)
        self.logger.addHandler(console_handler)

import os

# IMPORTANT: This file is meant to specify all the configuration values that
# are used by this application. While this configuration could be used directly
# It is intended that a "config.py" is created and a class is specified there
# that inherits from the Config class below. Values for the various settings
# would then be overridden in the child class and the child class used when
# running the parts of the symdash application.
__author__ = 'matt8057'


class Config(object):
    # Statement for enabling the development environment
    DEBUG = True
    DASHBOARD_HOST = '0.0.0.0'
    DASHBOARD_PORT = 8000

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Set the logs directory outside of our source directory
    LOGS_DIR = os.path.abspath(BASE_DIR)

    # Used if an email needs to be sent to the site administrator.
    ADMINS = frozenset(['youremail@yourdomain.com'])

    # Application threads. A common general assumption is using 2 per available
    # processor core - to handle incoming requests using one and performing
    # background operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection against Cross-site Request Forgery
    CSRF_ENABLED = True

    # Use a secure, unique and secret key for signing the data.
    CSRF_SESSOIN_KEY = 'secret csrf key'

    # Secret key for signing cookies
    SECRET_KEY = 'secret cookie key'

    MONGO_CONNECTION = 'mongodb://localhost:27017'

    LOG_FILE_NAME = 'unnamed'

    REPOSITORIES = [{'Owner': 'jquery',
                     'Name': 'jquery-ui',
                     'EnterpriseUrl': None,
                     'ApiKey': 'your_key_here'
                     },
                    {'Owner': 'fritogotlayed',
                     'Name': 'pyReleaseUtility',
                     'EnterpriseUrl': None,
                     'ApiKey': 'your_key_here'
                     }]

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError as e:
            raise ImportError(e)

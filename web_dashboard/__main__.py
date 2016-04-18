import sys

from web_dashboard.web.web_initializer import WebInitializer
from flask import Flask, render_template, request
from flask_injector import FlaskInjector, Injector
from os import path, linesep, makedirs
from logging import Logger, fatal, Formatter
from werkzeug.exceptions import NotFound
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from web_dashboard.web.siteroot.controller import mod as siteroot_module

CONFIG_TO_USE = 'config.Config'


def _install_secret_key(app, filename='secret_key'):
    """
    """
    filename = path.join(app.instance_path, filename)
    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        msg = 'No secret key installed.' + linesep
        full_path = path.dirname(filename)
        if not path.isdir(full_path):
            msg += 'mkdir -p {0}'.format(full_path)
        msg += 'head -c 24 /dev/urandom > {0}'.format(full_path)
        fatal(msg)


def _build_app(config_to_use,
               template_folder='web/templates',
               static_folder='web/static'):
    """
    """

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)
    app.config.from_object(config_to_use)

    if not app.config['DEBUG']:
        _install_secret_key(app)

    _setup_database(app.config)

    app.register_blueprint(siteroot_module)

    injector_ = Injector([WebInitializer(app)])
    FlaskInjector(app=app, injector=injector_)

    logger = injector_.get(Logger)  # type: Logger
    logger.info('Application initialized. "{0}" used.'.format(config_to_use))

    # Use a generic anonymous function to handle logging 404s
    @app.errorhandler(NotFound)
    @app.errorhandler(404)
    def not_found(error):
        logger.warning('Error "{0}" occurred. Url: {1}'.format(
            error, request.url
        ))

        return render_template('404.html'), error.code

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception('Error occurred in request to url: {0}'.format(
            request.url), exec_info=error)

        # Use 200 so flask doesn't use it's internal 500 handler
        return render_template('500.html'), 200

    return app


def _setup_database(config):
    """
    :type db: Database
    """
    client = MongoClient(config['MONGO_CONNECTION'])
    col = client['pyReleaseUtil'].reports  # type: Collection
    col.create_index("createdAt", expireAfterSeconds=900)


def main(argv):
    """
    Starts the application. If command line configuration is provided that
    configuration is used, else a default is used.
    """
    config = argv[0] if len(argv) > 0 else CONFIG_TO_USE

    app = _build_app(config)

    app.run(host=app.config['DASHBOARD_HOST'],
            port=app.config['DASHBOARD_PORT'],
            debug=app.config['DEBUG'])

if __name__ == '__main__':
    main(sys.argv[1:])

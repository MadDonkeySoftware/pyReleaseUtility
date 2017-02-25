import os
import sys
import pymongo
import logging
from os import path, linesep
import gevent.wsgi
from web_dashboard import logging_wrapper
import yaml

from flask import Flask, render_template, request
from pymongo import MongoClient
from pymongo.collection import Collection
from werkzeug.exceptions import NotFound

from web_dashboard.web.siteroot.controller import mod as siteroot_module

CONFIG_TO_USE = 'config.Config'
ENV_VAR_KEY = 'PY_RELEASE_UTIL_CONFIG'


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
        logging.fatal(msg)


def _build_app(config_to_use,
               template_folder='web/templates',
               static_folder='web/static'):

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)

    app.config.from_object(config_to_use)
    try:
        app.config.from_envvar(ENV_VAR_KEY)
    except RuntimeError:
        pass

    if not app.config['DEBUG']:
        _install_secret_key(app)

    app.register_blueprint(siteroot_module)

    logging_wrapper.initialize(app.config, app)
    logger = logging_wrapper.get_logger()
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

    # Import repositories
    _import_repositories(app)

    return app


def _setup_database(config):
    """
    :type config: flask.Config
    """
    client = MongoClient(config['MONGO_CONNECTION'])
    col = client['pyReleaseUtil'].reports  # type: Collection
    col.create_index([('key', pymongo.ASCENDING)])
    col.create_index('createdAt', expireAfterSeconds=900)


def _import_repositories(app):
    loc = os.environ.get('RELEASE_UTIL_REPOSITORIES_CONFIG', None)
    if loc is None:
        loc = 'repositories.yml'
        logger = logging_wrapper.get_logger()
        logger.warning(
            'Could not find environment variable '
            'RELEASE_UTIL_REPOSITORIES_CONFIG. Using default value of '
            '"{location}".'.format(location=loc)
        )
    with open(loc, 'r') as f:
        doc = yaml.load(f)
        app.config['REPOSITORIES'] = doc['repositories']


def main(argv):
    """
    Starts the application. If command line configuration is provided that
    configuration is used, else a default is used.
    """
    config = argv[0] if len(argv) > 0 else CONFIG_TO_USE

    app = _build_app(config)

    if app.config['SETUP_DB']:
        _setup_database(app.config)

    if app.config['DEBUG']:
        app.run(host=app.config['DASHBOARD_HOST'],
                port=app.config['DASHBOARD_PORT'],
                debug=True)
    else:
        http_server = gevent.wsgi.WSGIServer((app.config['DASHBOARD_HOST'],
                                              app.config['DASHBOARD_PORT']),
                                             app)
        http_server.serve_forever()

if __name__ == '__main__':
    main(sys.argv[1:])

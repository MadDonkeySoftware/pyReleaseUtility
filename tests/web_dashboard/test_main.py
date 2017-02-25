import flask
import unittest
import mock

import web_dashboard.server


class TestStringMethods(unittest.TestCase):

    def test_app_builds_properly(self):
        with mock.patch('web_dashboard.server._import_repositories'):
            app = web_dashboard.server._build_app(
                web_dashboard.server.CONFIG_TO_USE)
            self.assertIsNotNone(app)
            self.assertIsInstance(app, flask.Flask)

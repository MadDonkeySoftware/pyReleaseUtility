import flask
import unittest

import web_dashboard.__main__


class TestStringMethods(unittest.TestCase):

    def test_app_builds_properly(self):
        app = web_dashboard.__main__._build_app(web_dashboard.__main__.CONFIG_TO_USE)
        self.assertIsNotNone(app)
        self.assertIsInstance(app, flask.Flask)

from pip.req import parse_requirements
from setuptools import setup
# https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/

__author__ = 'matt8057'

dashboard_req_contents = parse_requirements('requirements.txt', session=False)
dashboard_req = [str(ir.req) for ir in dashboard_req_contents]


setup(
    # App Name
    name='pyReleaseUtil',

    # Version Number
    version='0.0.1',

    # Application Author
    author="MadDonkey Software",

    packages=['web_dashboard',
              'web_dashboard.web',
              'web_dashboard.web.siteroot'],
    install_requires=dashboard_req,
    entry_points={
        'web_dashboard': [
            'dashboard = src.web_dashboard.run:main'
        ]
    },
)

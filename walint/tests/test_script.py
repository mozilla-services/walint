import unittest
import os
from walint.core import main


_CFG = os.path.join(os.path.dirname(__file__), 'walint.cfg')


def setup(app, config):
    pass


def teardown(app, config):
    pass


def add_auth_header(app, config):
    pass


def cleanup_stuff(app, config):
    pass


def customctrl(method, service, app, caller):
    """Make sure the app does this or that"""
    res = caller(service.path)
    return res.status_int == 200


def customctrl2(method, service, app, caller):
    """Make sure the app does tea"""
    return False


class TestWalint(unittest.TestCase):

    def test_script(self):
        main(_CFG)

import unittest
import os
from walint.core import main


_CFG = os.path.join(os.path.dirname(__file__), 'walint.cfg')


def setup(app):
    pass


def teardown(app):
    pass


def add_auth_header(app):
    pass


def cleanup_stuff(app):
    pass


def customctrl(app, path, method):
    """Make sure the app does this or that"""
    return True


def customctrl2(app, path, method):
    """Make sure the app does tea"""
    return False



class TestWalint(unittest.TestCase):

    def test_script(self):
        main(_CFG)


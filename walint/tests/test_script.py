import unittest
import os
from walint.core import main


_CFG = os.path.join(os.path.dirname(__file__), 'walint.cfg')


def walint_setup():
    pass


def walint_teardown():
    pass


class TestWalint(unittest.TestCase):

    def test_script(self):
        main(_CFG)

        # assert global setup/teardown are called, and only once

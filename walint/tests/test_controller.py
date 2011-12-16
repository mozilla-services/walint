from unittest import TestCase

from webtest import TestApp

from walint import controllers
from walint.tests.testapp import application
from walint.util import CatchErrors
from walint.config import Service

app = TestApp(CatchErrors(application))


class TestController(TestCase):

    def test_basic_auth(self):
        # the controller should test wrong credentials fails
        # and good ones works
        ret = controllers.auth_basic("get",
                   Service("bar", "/bar", ["GET", "POST"]),
                   app, app.get, {}, ('foo', 'bar'))
        self.assertTrue(ret)

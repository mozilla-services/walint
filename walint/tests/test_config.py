from unittest import TestCase
import io

from walint.config import WalintParser, WalintTestCase, Service, Controller
from walint.util import METHS

_SAMPLE_CONFIG = """
[controller:ctrl1]
location = test
params = p1 p2
global_option = value
global_option2 = value2

[controller:ctrl2]
location = test

[service:foo]
path = /foo
methods = GET

[service:bar]
path = /bar
methods = GET|PUT
params = foo bar

[service:baz]
path = /baz
methods = *

[test:testone]
setup = walint.tests.test_config.foo
teardown = walint.tests.test_config.foo

services =
    foo GET
    bar *

controllers =
     ctrl1 param1 param2

[test:test2]
services = * *
controllers = *

[test:test3]
services = ~foo|~baz *
controllers = ~ctrl1
"""


def test_controller(*args, **kwargs):
    """This is a test controller"""
    return True


def foo():
    pass


class TestConfig(TestCase):

    def test_controller(self):
        controller = Controller("alias", ["param1", "param2"],
                                "walint.tests.test_config.test_controller",
                                foo="bar", baz="test")

        self.assertEquals(controller.params, ['param1', 'param2'])
        self.assertEquals(controller.func, test_controller)
        self.assertTrue(set(controller.options.values()), set(("bar", "test")))
        self.assertTrue(controller.description, 'This is a test controller')

    def test_controller_config(self):
        config = WalintParser()
        config.readfp(io.BytesIO(_SAMPLE_CONFIG))

        controller = Controller.from_config(config, "controller:ctrl1")
        self.assertEquals(controller.alias, "ctrl1")
        self.assertEquals(controller.location, "test")
        self.assertTrue("global_option" in controller.options.keys())
        self.assertEqual(controller.options["global_option"], "value")
        self.assertEqual(controller.params, ["p1", "p2"])

    def test_service_config(self):
        config = WalintParser()
        config.readfp(io.BytesIO(_SAMPLE_CONFIG))

        service = Service.from_config(config, "service:bar")
        self.assertEquals(service.path, "/bar")
        self.assertEquals(service.methods, ["GET", "PUT"])
        self.assertEquals(service.params, ['foo', 'bar'])

    def test_test_config(self):
        config = WalintParser()
        config.readfp(io.BytesIO(_SAMPLE_CONFIG))

        test = WalintTestCase.from_config(config, "test:testone")
        self.assertEquals(test.name, "testone")
        self.assertEqual(test.setup, foo)
        self.assertEqual(test.teardown, foo)
        self.assertEqual(test.services, [("foo", ["GET", ]), ("bar", METHS)])
        self.assertEqual(test.controllers, [("ctrl1", ["param1", "param2"]), ])

        # test we expand "* *" the right way
        test2 = WalintTestCase.from_config(config, "test:test2")
        self.assertEqual(len(config.get_services()), len(test2.services))
        self.assertEqual([i[1] for i in test2.services][0], METHS)

        # * should work as well for controllers
        self.assertEqual(len(config.get_controllers()), len(test2.controllers))

        # test exclusion works with ~
        # ... for services
        test3 = WalintTestCase.from_config(config, "test:test3")
        self.assertFalse("foo" in dict(test3.services).keys())
        self.assertFalse("baz" in dict(test3.services).keys())

        # ... and for controllers
        self.assertTrue("ctrl1" not in dict(test3.controllers).keys())

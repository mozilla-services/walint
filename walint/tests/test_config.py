from unittest import TestCase
import io

from walint.config import WalintParser, WalintTestCase, Service, Controller

_SAMPLE_CONFIG = """
[controller:ctrl1]
location = test
global_option = value
global_option2 = value2

[service:bar]
path = /bar
methods = GET|PUT

[test:testone]
setup = walint.tests.test_config.foo
teardown = walint.tests.test_config.foo

services =
    foo GET
    bar *

controllers =
     ctrl1 param1 param2
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

    def test_service_config(self):
        config = WalintParser()
        config.readfp(io.BytesIO(_SAMPLE_CONFIG))

        service = Service.from_config(config, "service:bar")
        self.assertEquals(service.path, "/bar")
        self.assertEquals(service.methods, ["GET", "PUT"])

    def test_test_config(self):
        config = WalintParser()
        config.readfp(io.BytesIO(_SAMPLE_CONFIG))

        test = WalintTestCase.from_config(config, "test:testone")
        self.assertEquals(test.name, "testone")
        self.assertEqual(test.setup, foo)
        self.assertEqual(test.teardown, foo)
        self.assertEqual(test.services, [("foo", ["GET", ]), ("bar", ["*", ])])
        self.assertEqual(test.controllers, [("ctrl1", ["param1", "param2"]), ])

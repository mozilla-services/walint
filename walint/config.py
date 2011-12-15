from ConfigParser import ConfigParser, NoOptionError
from walint.util import resolve_name, METHS

_CONTROLLER_KEYS = ("location", "setup", "teardown")
_SERVICES_KEYS = ("path", "methods", "setup", "teardown")
_TEST_KEYS = ("setup", "teardown", "services", "controllers")


class SetupTearDownMixin(object):
    def __init__(self, setup=None, teardown=None):
        self._setup = setup
        self._teardown = teardown

    @property
    def setup(self):
        return resolve_name(self._setup) if self._setup else None

    @setup.setter
    def setup(self, value):
        self._setup = value

    @property
    def teardown(self):
        return resolve_name(self._teardown) if self._teardown else None

    @teardown.setter
    def teardown(self, value):
        self._teardown = value


class Test(SetupTearDownMixin):
    def __init__(self, name, controllers=None, services=None, *args, **kwargs):
        self.name = name
        self.controllers = controllers or []
        self.services = services or []
        super(Test, self).__init__(*args, **kwargs)

    @classmethod
    def from_config(cls, config, section):
        _, name = section.split(':')

        test = cls(name)
        test.setup = config.get(section, "setup")
        test.teardown = config.get(section, "teardown")

        # get the list of services
        services = config.get(section, "services") or "* *"
        services = services.split('\n')

        for service in services:
            if service:
                name, methods = service.split(" ")
                test.services.append((name, methods.split('|')))
                # XXX handle wildcards

        controllers = config.get(section, "controllers") or ""
        controllers = controllers.split("\n")

        for controller in controllers:
            if controller:
                temp = controller.split(" ")
                alias, params = temp[0], temp[1:]
                test.controllers.append((alias, params))

        return test


class Service(SetupTearDownMixin):
    def __init__(self, name, path, methods, *args, **kwargs):
        self.name = name
        self.path = path
        self.methods = methods
        super(Service, self).__init__(*args, **kwargs)

    @classmethod
    def from_config(cls, config, section):
        _, name = section.split(':')

        path = config.get(section, 'path')
        methods = config.get(section, 'methods')
        if methods:
            methods = methods.split("|")
        else:
            methods = METHS

        return cls(name, path, methods)


class Controller(SetupTearDownMixin):
    def __init__(self, alias, params=None, location=None, setup=None,
                 teardown=None, **options):
        self.alias = alias
        self.params = params
        self.location = location
        self.options = options
        self._description = None
        self._func = None
        super(Controller, self).__init__(setup, teardown)

    @property
    def description(self):
        if self._description is None:
            func = self.func
            if func.__doc__ is not None:
                desc = func.__doc__
            else:
                desc = func.__name__
            self._description = desc
        return  self._description

    @property
    def func(self):
        if self._func is None:
            self._func = resolve_name(self.location)
        return self._func

    @property
    def methods(self):
        """If the callable is defined and only lists some methods, use them,
        otherwise return the default HTTP methods"""
        return getattr(self.func, '_accepted_methods', METHS)

    @classmethod
    def from_config(cls, config, section):
        _, alias = section.split(':')

        location = config.get(section, 'location')

        # read the optional options passed to the section
        keys = [option for option in config.options(section)
                   if option not in _CONTROLLER_KEYS]

        options = {}
        for key in keys:
            options[key] = config.get(section, key)

        return cls(alias, location=location, **options)


class NamespacedConfigParser(ConfigParser):
    """The configuration parser, with some fancy methods to ease its use
    with namespaces"""

    def sections(self, namespace=None, return_name=False):
        if namespace is None:
            return self.sections()
        else:
            # return the FQN if needed
            if return_name:
                _return = lambda x: (x, x.split(':')[1])
            else:
                _return = lambda x: x

            return [_return(section) for section in ConfigParser.sections(self)
                    if namespace == section.split(':')[0]]

    def get(self, section, key, default=None, *args, **kwargs):
        """redefines the get method to default to None"""
        try:
            return ConfigParser.get(self, section, key, *args, **kwargs)
        except NoOptionError:
            return default


class WALintParser(NamespacedConfigParser):
    """Provides facilities to access the WALint configuration files.
    Also, some access is cached to avoid parsing the INI file multiple times
    """
    def __init__(self, *args, **kwargs):
        self._services = {}
        self._controllers = {}
        self._tests = {}
        return NamespacedConfigParser.__init__(self)

    def get_service(self, name):
        if not name in self._services:
            self._services[name] = \
                    Service.from_config(self, 'service:%s' % name)
        return self._services[name]

    def get_controller(self, name):
        if not name in self._controllers:
            self._controllers[name] = \
                    Controller.from_config(self, 'controller:%s' % name)
        return self._controllers[name]

    def get_test(self, name):
        if not name in self._tests:
            self._tests[name] = \
                    Test.from_config(self, 'test:%s' % name)
        return self._tests[name]

    def services(self):
        if not self._services:
            for section, name in self.sections(namespace="service",
                    return_name=True):
                self.get_service(name)
        return self._services

    def controllers(self):
        if not self._controllers:
            for section, name in self.sections(namespace="controller",
                    return_name=True):
                self.get_controller(name)
        return self._controllers

    def tests(self):
        if not self._tests:
            for section, name in self.sections(namespace="test",
                    return_name=True):
                self.get_test(name)
        return self._tests

    def root_options(self, section="walint"):
        return dict(self.items(section))

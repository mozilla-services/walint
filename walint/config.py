from ConfigParser import ConfigParser, NoOptionError
from functools import partial

from walint.util import resolve_name, METHS

_CONTROLLER_KEYS = ("location", "setup", "teardown", "params")
_SERVICES_KEYS = ("path", "methods", "setup", "teardown")
_TEST_KEYS = ("setup", "teardown", "services", "controllers", "singles")


def get_controllers(config, section, key="controller"):

    controller_list = []

    # and the list of controllers
    controllers = config.get(section, "%ss" % key) or ""
    controllers = map(str.strip, controllers.split("\n"))

    for controller in controllers:
        if controller:
            if controller.startswith("*") or\
                    controller.startswith("~"):
                aliases = config.get_namespace(key).keys()
                if controller.startswith("~"):
                    exclude = [n.strip().strip("~")
                               for n in controller.split("|")]
                    aliases = set(aliases) - set(exclude)
                for alias in aliases:
                    controller_list.append((alias, []))
            else:
                temp = controller.split()
                alias, params = temp[0], temp[1:]
                controller_list.append((alias, params))

    return controller_list


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


class WalintTestCase(SetupTearDownMixin):
    def __init__(self, name, controllers=None, services=None, *args, **kwargs):
        super(WalintTestCase, self).__init__(*args, **kwargs)
        self.name = name
        self.controllers = controllers or []
        self.services = services or []

    @classmethod
    def from_config(cls, config, section):

        _, name = section.split(':', 1)

        testcase = cls(name)
        testcase.setup = config.get(section, "setup")
        testcase.teardown = config.get(section, "teardown")

        # get the list of services
        services = config.get(section, "services") or "* *"
        services = services.split('\n')

        for service in services:
            if service:
                name, methods = service.split()

                if name == "*" or name.startswith("~"):
                    # we want to test all the services
                    names = config.get_services().keys()
                    if name.startswith("~"):
                        # filter the listed ones
                        exclude = [n.strip().strip("~")
                                   for n in name.split("|")]

                        names = set(names) - set(exclude)
                else:
                    names = map(str.strip, name.split("|"))

                if methods.startswith("~"):
                    exclude = [m.strip().strip("~")
                               for m in methods.split("|")]
                    methods = set(METHS) - set(exclude)

                elif methods == "*":
                    methods = METHS
                else:
                    methods = [m.strip()for m in methods.split("|")]

                for name in names:
                    testcase.services.append((name, methods))

        # get the list of controllers and singles
        testcase.controllers = get_controllers(config, section, "controller")
        testcase.singles = get_controllers(config, section, "single")

        return testcase


class Service(SetupTearDownMixin):
    def __init__(self, name, path, methods, options=None, *args, **kwargs):
        self.name = name
        self.path = path
        self.methods = methods
        self.options = options or {}
        super(Service, self).__init__(*args, **kwargs)

    @classmethod
    def from_config(cls, config, section):
        _, name = section.split(':')

        path = config.get(section, 'path')
        methods = config.get(section, 'methods')
        if methods:
            methods = map(str.strip, methods.split("|"))
        else:
            methods = METHS

        keys = [option for option in config.options(section)
                   if option not in _SERVICES_KEYS]

        options = {}
        for key in keys:
            options[key] = config.get(section, key)
        
        return cls(name, path, methods, options)


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
        params = config.get(section, 'params', [])
        if params:
            params = params.split()

        # read the optional options passed to the section
        keys = [option for option in config.options(section)
                   if option not in _CONTROLLER_KEYS]

        options = {}
        for key in keys:
            options[key] = config.get(section, key)

        return cls(alias, params=params, location=location, **options)


class Single(Controller):
    """A controller which run only once per serie of tests"""


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


class WalintParser(NamespacedConfigParser):
    """Provides facilities to access the WALint configuration files.
    Also, some access is cached to avoid parsing the INI file multiple times
    """
    def __init__(self, *args, **kwargs):
        self._classes = {'test': WalintTestCase,
                         'controller': Controller,
                         'service': Service,
                         'single': Single}

        # aliases
        self.get_tests = partial(self.get_namespace, "test")
        self.get_services = partial(self.get_namespace, "service")
        self.get_singles = partial(self.get_namespace, "single")
        self.get_controllers = partial(self.get_namespace, "controller")

        self.get_test = partial(self.get_prefixed, "test")
        self.get_controller = partial(self.get_prefixed, "controller")
        self.get_service = partial(self.get_prefixed, "service")
        self.get_single = partial(self.get_prefixed, "single")

        return NamespacedConfigParser.__init__(self)

    def get_prefixed(self, prefix, name):
        _prefix = "_%ss" % prefix
        if not hasattr(self, _prefix):
            setattr(self, _prefix, {})

        elements = getattr(self, _prefix)
        if not name in elements:
            elements[name] = self._classes.get(prefix)\
                    .from_config(self, "%s:%s" % (prefix, name))
        return elements

    def get_namespace(self, namespace):
        if not hasattr(self, "_%ss" % namespace):
            for section, name in self.sections(namespace=namespace,
                    return_name=True):
                self.get_prefixed(namespace, name)
        return getattr(self, "_%ss" % namespace, {})

    def root_options(self, section="walint"):
        return dict(self.items(section))

import sys
from ConfigParser import ConfigParser, NoOptionError
import random
import string

from webtest import TestApp


def _resolve_name(name):
    ret = None
    parts = name.split('.')
    cursor = len(parts)
    module_name = parts[:cursor]
    last_exc = None

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name))
            break
        except ImportError, exc:
            last_exc = exc
            if cursor == 0:
                raise
            cursor -= 1
            module_name = parts[:cursor]

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError:
            if last_exc is not None:
                raise last_exc
            raise ImportError(name)

    if ret is None:
        if last_exc is not None:
            raise last_exc
        raise ImportError(name)

    return ret

OK = '\033[92m'
FAIL = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'


def _default_stream(msg, path, method, success=True):
    path = BLUE + '%s %s' % (method, path) + ENDC
    if success:
        print(OK + '[OK] '+ ENDC + path + ' ' + msg)
    else:
        print(FAIL + '[KO] '+ ENDC + path + ' ' + msg)

def run(app, controllers, services, stream_result=None):
    results = []
    if stream_result is None:
        stream_result = _default_stream

    for name, controller in controllers:
        msg = controller.__doc__
        if msg is None:
            msg = name

        for path, methods, setup, teardown in services:
            for method in methods:
                if setup is not None:
                    setup(app)
                try:
                    success = controller(app, path, method)
                    stream_result(msg, path, method, success)
                    results.append((success, msg))
                finally:
                    if teardown is not None:
                        teardown(app)

    return results


def load_config(file):
    config = ConfigParser()
    config.read(file)
    return config


def build_app(config):
    app = config.get('walint', 'root')
    if app.startswith('http'):
        raise NotImplementedError()
    return TestApp(_resolve_name(app))


def _random_path(size=10):
    return '/' + ''.join([random.choice(string.ascii_letters)
                          for l in range(size)])


def _resolve_ctrl(fqn):
    return fqn, _resolve_name(fqn)


def get_services(config):
    svcs = config.get('walint', 'services')
    svcs = [svc for svc in
                [svc.strip() for svc in svcs.split('\n')]
             if svc != '']

    res = []
    for svc in svcs:
        path = config.get(svc, 'path')
        if path == '?':
            path = _random_path()
        methods = [meth.strip() for meth in
                    config.get(svc, 'methods').split('|')
                   if meth.strip() != '']
        if methods == ['*']:
            methods = ['GET', 'PUT', 'HEAD', 'DELETE', 'POST',
                       'OPTIONS', 'TRACE', 'CONNECT']
        try:
            setup = _resolve_name(config.get(svc, 'setup'))
        except NoOptionError:
            setup = None
        try:
            teardown = _resolve_name(config.get(svc, 'teardown'))
        except NoOptionError:
            teardown = None

        res.append((path, methods, setup, teardown))
    return res


def get_controllers(config):
    ctrls = config.get('walint', 'controllers')
    return  [_resolve_ctrl(ctrl) for ctrl in
                [ctrl.strip() for ctrl in ctrls.split('\n')]
             if ctrl != '']


def main(file):
    # load the config
    config = load_config(file)

    try:
        stream = config.get('walint', 'stream')
    except NoOptionError:
        stream = None

    # creating the app client
    app = build_app(config)

    # getting the list of controllers
    controllers = get_controllers(config)

    # getting the list of services to test
    services = get_services(config)

    # now running the tests
    results = run(app, controllers, services, stream)

    return results


if __name__ == '__main__':
    results = main(sys.argv[1])
    sys.exit(len(results) != 0)


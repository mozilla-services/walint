import random
import string
import functools

from webob.dec import wsgify
from webob.exc import HTTPException

# TRACE and CONNECT not supported
METHS = ('GET', 'PUT', 'HEAD', 'DELETE', 'POST',
         'OPTIONS')


def random_path(size=10):
    return '/' + ''.join([random.choice(string.ascii_letters)
                          for l in range(size)])


def accept(methods):
    """Decorator to list the accepted methods for a controller.

    Internally, it adds the list of accepted methods to the
    function by attaching an _accepted_methods list to the
    decorated function
    """
    def wrapper(f):
        setattr(f, '_accepted_methods', methods)

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapped
    return wrapper


def default_stream(msg, path=None, method=None, success=True):

    OK = '\033[92m'
    FAIL = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

    if path is not None:
        path = BLUE + '%s %s ' % (method, path) + ENDC
    else:
        path = ''

    if success:
        print(OK + '[OK] ' + ENDC + path + msg)
    else:
        print(FAIL + '[KO] ' + ENDC + path + msg)


def resolve_name(name):
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


class CatchErrors(object):
    def __init__(self, app):
        self.app = app
        if hasattr(app, 'registry'):
            self.registry = app.registry

    @wsgify
    def __call__(self, request):
        try:
            return request.get_response(self.app)
        except HTTPException, e:
            return e

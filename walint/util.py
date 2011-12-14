import random
import string
import functools

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

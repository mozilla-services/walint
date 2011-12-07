import random
import string

# TRACE and CONNECT not supported
METHS = ('GET', 'PUT', 'HEAD', 'DELETE', 'POST',
         'OPTIONS')


def random_path(size=10):
    return '/' + ''.join([random.choice(string.ascii_letters)
                          for l in range(size)])

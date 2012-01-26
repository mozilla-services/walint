""" Default controllers """
import base64

from webtest.app import TestRequest

from walint.util import accept, _err


@accept(["POST", "PUT"])
def json_breaker(method, service, app, caller, config):
    """Sending a broken JSON object returns a 400"""

    bomb = {}
    for param in service.params:
        bomb[param] = "{test:json]"  # aouch!

    expected_status = 400 if bomb else 200
    return _err(caller, service.path, params=bomb, status=expected_status)


def auth_basic(method, service, app, caller, config, credentials=None):
    """basic authentication"""
    if credentials is not None and len(credentials) == 2:
        username, password = credentials
    elif 'username' in config and 'password' in config:
        username = config['username']
        password = config['password']
    else:
        raise Exception("You must specify some authentication in the "
            "configuration, either by using the 'username' and 'password' "
            "global configuration settings, or by passing the parameters to "
            "the controller")

    # not being authenticated should return a 401
    if not _err(caller, service.path, status=401):
        return False

    # let's generate the hash
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]

    # an authenticated request should work and return something else,
    # starting by # 2xx or 3xx
    return _err(caller, service.path,
                headers={"Authorization": "Basic %s" % base64string},
                status=200)


def auth_breaker(method, service, app, caller, config):
    """Broken authorization headers returns a 400"""
    return _err(caller, service.path, headers={"Authorization": "yeah!"},
                status=400)


def check_406(method, service, app, caller, config):
    """Unsupported Content-Type values in the headers returns a 406"""
    return _err(caller, service.path, headers={"Accept": "cheese"},
            status=406)


@accept(["PUT", "POST"])
def check_411(method, service, app, caller, config):
    """Missing content-length on PUT or POST returns a 411"""
    class PatchedRequest(TestRequest):
        """Patched to remove Content-Length"""
        @classmethod
        def blank(cls, path, environ=None, **kw):
            environ.pop('CONTENT_LENGTH')
            return super(PatchedRequest, cls).blank(path, environ, *kw)

    # monkey patch!
    _old = app.RequestClass
    app.RequestClass = PatchedRequest
    try:
        return _err(caller, service.path, params={"test": "yay"}, status=411)
    finally:
        app.RequestClass = _old


@accept(["PUT", "POST"])
def check_413(method, service, app, caller, config, params=[]):
    """Large PUT|POST returns a 413"""
    size = int(params[0] if len(params) > 0 else 3)
    big_string = u"a" * 1048613 * size  # "a" is about 1 byte.
    return _err(caller, service.path, params={"test": big_string}, status=413)


def check_414(method, service, app, caller, config, params=[]):
    """Checks that uri > 4096 generates a 414"""
    size = int(params[0] if len(params) > 0 else 5000)
    path = service.path + '?' + 'o' * size + '=1'
    return _err(caller, path, status=414)

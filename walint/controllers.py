""" Default controllers """
import base64

from walint.util import accept, _err


def check_414(method, service, app, caller, config):
    """Checks that uri > 4096 generates a 414"""
    path = service.path + '?' + 'o' * 5000 + '=1'
    return _err(caller, path, status=414)


@accept(["POST", "PUT"])
def broken_json(method, service, app, caller):
    """Sending a broken JSON object returns a 400"""
    # getting info from the service being tested: which parameter should
    # be used?
    pass


def auth_basic(method, service, app, caller, config, credentials=None):
    """basic authentication"""
    if credentials is not None and len(credentials) == 2:
        username, password = credentials
    elif 'username' in config and 'password' in config:
        username = config['usernam']
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

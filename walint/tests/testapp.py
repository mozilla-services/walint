from webob.dec import wsgify
from webob import exc

from paste.auth.basic import AuthBasicAuthenticator

_SERVICES_PATHS = ('/public', '/baz', '/boh', '/bar')
_USERNAME = "foo"
_PASSWORD = "bar"


def ok(request):
    return "ok"


def need_auth(request):
    auth = AuthBasicAuthenticator("walint", check_credentials)
    username = auth(request.environ)
    if username == _USERNAME:
        return ok(request)
    return username


def check_credentials(environ, username, password):
    return username == _USERNAME and password == _PASSWORD


#A mapping of (paths, method) to callables
_ROUTES = {
        ('/bar', 'GET'): need_auth,
        ('/baz', 'PUT'): need_auth,
        ('/baz', 'POST'): need_auth,
}


class App(object):
    """A wsgi application to run the tests.  """

    @wsgify
    def __call__(self, request):
        if len(request.path_info + request.query_string) > 4096:
            return exc.HTTPRequestURITooLong()

        if not request.path_info in _SERVICES_PATHS:
            return exc.HTTPNotFound()

        func = _ROUTES.get((request.path_info, request.method), ok)
        return func(request)


application = App()

import json
from wsgiref.simple_server import make_server

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
    try:
        username = auth(request.environ)
    except ValueError:
        return exc.HTTPBadRequest()

    if username == _USERNAME:
        return ok(request)
    return username


def check_credentials(environ, username, password):
    return username == _USERNAME and password == _PASSWORD


def consume_params(request):
    # we want to deserialize "heh" and "yeah".
    if 'application/json' in request.accept:
        for param in request.params.keys():
            try:
                json.loads(request.params[param])
            except ValueError:
                return  exc.HTTPBadRequest()
        return ok(request)
    else:
        raise exc.HTTPNotAcceptable()

#A mapping of (paths, method) to callables
_ROUTES = {
        ('/bar', 'GET'): need_auth,
        ('/bar', 'PUT'): consume_params,
        ('/bar', 'POST'): consume_params,
        ('/baz', 'PUT'): need_auth,
        ('/baz', 'POST'): need_auth,
}


class App(object):
    """A wsgi application to run the tests.  """

    @wsgify
    def __call__(self, request):
        if len(request.path_info + request.query_string) > 4096:
            return exc.HTTPRequestURITooLong()
        
        if request.method in ['PUT', 'POST']:
            if 'Content-Length' in request.headers and\
                    int(request.headers['Content-Length']) > 3145728:
                return exc.HTTPRequestEntityTooLarge()

            elif 'Content-Length' not in request.headers:
                return exc.HTTPLengthRequired()

        if not request.path_info in _SERVICES_PATHS:
            return exc.HTTPNotFound()

        func = _ROUTES.get((request.path_info, request.method))
        if func is not None:
            return func(request)
        else:
            return exc.HTTPMethodNotAllowed()


application = App()

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print "Serving HTTP on port 8000..."
    httpd.serve_forever()

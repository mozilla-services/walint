from webob.dec import wsgify
from webob import exc
from wsgiref.simple_server import make_server


class App(object):

    @wsgify
    def __call__(self, request):
        if len(request.path_info + request.query_string) > 4096:
            return exc.HTTPRequestURITooLong()

        if not request.path_info in ('/foo', '/baz', '/boh'):
            return exc.HTTPNotFound()
        return 'ok'


application = App()


from webob.dec import wsgify
from webob import exc
from wsgiref.simple_server import make_server


class App(object):

    @wsgify
    def __call__(self, request):
        if not request.path_info in ('/foo', '/baz', '/boh'):
            return exc.HTTPNotFound()
        return 'ok'


application = App()


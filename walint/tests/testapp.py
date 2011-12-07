from webob.dec import wsgify
from wsgiref.simple_server import make_server


class App(object):

    @wsgify
    def __call__(self, request):
        return 'ok'


application = App()


from wsgiref.simple_server import make_server, demo_app

application = make_server('', 8000, demo_app)


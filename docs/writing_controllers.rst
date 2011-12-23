Writing Controllers
===================

Tests are provided by controllers. A controller receives as arguments the HTTP 
method, the service, the app (a `webtest.TestApp` object which 
can be used to make queries on the wsgi layer), a caller, the shortcut to the 
test method, the configuration object ans some optional arguments.

Here is an example definition of a controller::

    def teapot(method, service, app, caller, config, *args):
        """Check that the app does tea"""
        # do the test
        return True

Docstrings are used by the runner so you can get some detailed info about
what's happening.

Controllers return `True` on success and `False` on failure.

Singles
-------

You may like to run some tests only once. WAlint comes with so called
"single controllers". You can list them in the configuration file using the
`singles` configuration key of a `test` section::

    [test:test1]
    ; ...
    singles = walint.controllers.check_404

The signature is also different::

    def check_404(app, config, *params):
        pass

The app passed is the `webtest.TestApp` instance. You can use it to run queries
on the service under test (see `the webtest documentation <http://webtest.pythonpaste.org/en/latest/index.html>`_ 
for more information). The configuration is also passed, as well as any other
positional arguments you could have defined.
    

Filtering the accepted methods
------------------------------

Some controllers don't need to be run against each of the HTTP methods of the
service.

You can filter them using the `@accept` decorator available in `walint.utils`::

    @accept(["POST", "PUT"])
    def broken_json(method, path, app, caller):
        """Sending a broken JSON object returns a 400"""
        # do your stuff here and return




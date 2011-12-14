WALint
######

WALint (Web App Lint) is a tool for testing your web services against a set
of common HTTP metrics. The main goal is to test that your application does not
fail on some weird cases, and that it complies with the HTTP specification.

It is as simple as writing an `.ini` file and running `walint` on it. Here is
an example configuration file::

    [walint]
    root = walint.tests.testapp.application
    tests = walint.controllers.check_414
            walint.controllers.broken_json

    setup = walint.tests.test_script.setup
    teardown = walint.tests.test_script.teardown

    services = foo
               baz

    [foo]
    path = /foo
    methods = GET|POST|PUT
    setup = walint.tests.test_script.add_auth_header
    teardown = walint.tests.test_script.cleanup_stuff

    [baz]
    path = /baz
    methods = POST

Here, the `/foo` and `/baz` services will be tested against the tests listed in
the `tests` configuraton key.

Once installed, WALint provides a `walint` CLI script you can use to invoke
it::

    $ walint walint.cfg

WALint can run against WSGI endpoints and real URLs. If you specify a WSGI
endpoint, you can also specify the `PYTHON_PATH` to use in the configuration.

Writing Controllers
===================

Tests are provided by controllers. A controller receives as arguments the HTTP 
method, the path (to the resource), the app (a `webtest.TestApp` object which 
can be used to make queries on the wsgi layer) and a caller, the shortcut to the 
test method.

Here is an example definition of a controller::

    def check_414(method, path, app, caller):
        """Checks that uri > 4096 generates a 414"""
        # do the test
        return True

Docstrings are used by the runner so you can get some detailed info about
what's happening.

Controllers return `True` on success and `False` on failure.


Singles
-------

Some tests don't have to be run on each services. WAlint comes with so called
"single controllers". You can list them in the configuration file using the
`singles` configuration key of the `walint` section::

    [walint]
    ; ...
    singles = walint.controllers.check_404

The signature is also different::

    def check_404(app):
        pass

The app passed is the `webtest.TestApp` instance. You can use it to run queries
on the service under test (see `the webtest documentation <http://webtest.pythonpaste.org/en/latest/index.html>`_ 
for more information)
    

Filtering the accepted methods
------------------------------

Some controllers don't need to be run against each of the HTTP methods of the
service.

You can filter them using the `@accept` decorator available in `walint.utils`::

    @accept(["POST", "PUT"])
    def broken_json(method, path, app, caller):
        """Sending a broken JSON object returns a 400"""
        # do your stuff here and return

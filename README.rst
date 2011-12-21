WALint
######

WALint (Web App Lint) is a tool for testing your web services against a set
of common HTTP metrics. The main goal is to test that your application does not
fail on some weird cases, and that it complies with the HTTP specification.

WALint provides a `walint` CLI script you can use to invoke it::

    $ walint walint.cfg

It is as simple as writing an `.ini` file and running `walint` on it. Here is
an example configuration file::

    [walint]
    root = walint.tests.testapp.application

    ; you can define controllers with an alias so they are easy to use multiple
    ; times
    [controller:auth-basic]
    location = walint.controllers.auth_basic
    params = foo bar

    ; services defines paths and methods.
    [service:bar]
    path = /bar
    methods = GET|PUT|POST

    [service:baz]
    path = /baz
    methods = *

    [test:testauth]
    ; Test for basic authentication on bar and baz
    services =
        bar GET
        baz PUT|POST

    controllers = auth-basic

    ; singles are run only once (they get all the defined services
    ; as an argument and the configuration)
    singles = walint.singles.check_404

Here, the `/bar` and `/baz` services will be tested against basic
authentication, only for the specified methods.

Writing configuration
=====================

As you can see, there is a number of sections, some of them are prefixed by
`test`, `service` or `controller`.

You can define any number of services or controllers, and you then need to mix
them together when defining your tests.

The main section: [walint]
--------------------------

WALint can run against WSGI endpoints and real URLs, defined in the `walint`
section, by the `root` key. If you specify a WSGI endpoint, you can also 
specify the `PYTHON_PATH` to use in the configuration.

Services
--------

Services are defined by an name, a path and some methods. All the services
sections are prefixed by `service:`, like this::

    [service:bar]
    path = /bar
    methods = GET|PUT|POST

Here, all only the GET, PUT and POST methods are available on the *bar*
service, available at `/bar/`.

The methods values are separated by a pipe (`|`), you can also use a wildcard
(`*`) if you want all the methods to be used.

Controllers
-----------

Controllers are paths to python callables which are either returning `True` or
`False`, depending the issue of the test. You can specify a section for them if
needed but you are not forced to (sometimes, it's simpler to just specify the
location of the callable).

Controller sections are prefixed by `controller:` and can define:

* a location, the path the callable
* an alias, in the title of the section
* some parameters which would be passed to the controller when called

::

    [controller:auth-basic]
    location = walint.controllers.auth_basic
    params = foo bar

Here the alias of the controller is "auth-basic", and it can be used in
a *test* section, see below.


Tests
-----

Tests are the master piece of WALint, they define how you want to combine
services and controllers. Here is how you do it::

    [test:testauth]
    ; Test for basic authentication on bar and baz
    services =
        bar GET
        baz PUT|POST

    controllers = auth-basic

    ; singles are run only once (they get all the defined services
    ; as an argument and the configuration)
    singles = walint.singles.check_404

`services`, `controllers` and `singles` support multiple values, which have to
be separated by new lines. For instance, you may want to specify multiple
controllers like this::

    controllers = 
        auth-basic
        another-controller

You can also use wildcards for services and controllers.

* `*` means "everything"
* `~` means "but"

So you can define something like this::

    controllers = ~auth-basic

And all the controllers **defined in the configuration file** would match, except
this partitular one.

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


List of shipped controllers
===========================

WALint comes with a number of controllers to check your web service complies to
the HTTP specification. Here is a complete list so far:

walint.controllers.auth_basic
-----------------------------

Checks that the basic authentication works as expected. It checks that a call
without any authentication returns a **401 Unauthorized** and that a call with
the right credentials do work (200).

You can provide the credentials in two different ways: either by specifying
them directly when defining the controller in the documentation, like this::

    controllers = walint.controllers.auth_basic username password

Or, if you defined the controller in its own section, by specifying the params
key::

    [controller:auth_basic]
    location = walint.controllers.auth_basic
    params = username password

walint.controllers.json_breaker
-------------------------------

Sends some random invalid json objects to your server and checks it doesn't
make it crash. The server should return a **400 Bad Request**

This is only available for PUT and POST methods.

walint.controllers.auth_breaker
-------------------------------

Sends a broken authentication header on the server to check it doesn't make it
crash.

The server should return a **400 Bad Request**

walint.controllers.check_406
----------------------------

Checks that when sending invalid Accepted Content-Type values (we are only
accepting "cheese" here), the server returns a **406 Not Acceptable** with
the list of available choices.

walint.controllers.check_411
----------------------------

Try to send a request without the **Content-Length** header. The server should
answer with a **411 Length Required**.

Only works for the PUT and POST methods.

walint.controllers.check_413
----------------------------

Send large (see below) requests to the server, it should not parse them but
rather return a **413 Request Entity Too Large**.

Only works for POST and PUT methods

The size can be defined in the configuration, in MB, and defaults to 3MB.

walint.controllers.check_414
----------------------------

Send a  request to the server, with a "too long" URI, and and checks that the
server returns a **414 Request-URI Too Long**

The size of the request can be specified in the configuration. Default value is
5000.

walint.singles.check_404
------------------------

Send a request to a random URI. The result should be **404 Not Found**

walint.singles.check_405
------------------------

This controller goes trough all the defined services and find one which doesn't
define all the methods. If so, it tries to send a request to this service with
one of the missing verbs.

The server should answer with a **405 Method Not Allowed**

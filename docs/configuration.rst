Writing configuration
=====================

WALint uses a `.ini` file as configuration.

It is as simple as writing an `.ini` file and running `walint` on it. Here is
an example configuration file::

    [walint]
    root = walint.tests.testapp.application
    setup = walint.tests.test_script.walint_setup
    teardown = walint.tests.test_script.walint_teardown

    [controller:auth-basic]
    location = walint.controllers.auth_basic
    params = foo bar

    [service:bar]
    path = /bar
    methods = GET|PUT|POST
    params = yeah heh
    accept = application/json

    [service:baz]
    path = /baz
    methods = *

    [test:testauth]
    ; Test for basic authentication on bar and baz
    services =
        bar GET
        baz PUT|POST

    controllers = auth-basic
                  walint.controllers.auth_breaker

    [test:all]
    ; singles are run only once (they get all the defined services
    ; as an argument and a default contact
    singles = walint.singles.check_404
              walint.singles.check_405

    controllers = walint.controllers.json_breaker
                  walint.controllers.check_406
                  walint.controllers.check_411
                  walint.controllers.check_413 16

    services = bar POST|PUT

Here, the `/bar` and `/baz` services will be tested against basic
authentication, only for the specified methods.

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

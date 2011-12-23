WALint - Web Application Lint
=============================

WALint (Web App Lint) is a tool for testing your web services against a set
of common HTTP metrics. The main goal is to test that your application does not
fail on some weird cases, and that it complies with the HTTP specification.

Here's a sample configuration file::

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

WALint provides a `walint` CLI script you can use to invoke it::

    $ walint walint.cfg

And get a result like this::

    [OK] [all] Non-existant paths return a 404
    [OK] [all] Wrong HTTP method on a right URI returns a 405
    [OK] POST /bar [all] Sending a broken JSON object returns a 400/200
    [OK] POST /bar [all] Unsupported Content-Type values in the headers returns a 406
    [OK] POST /bar [all] Missing content-length on PUT or POST returns a 411
    [OK] POST /bar [all] Large PUT|POST returns a 413
    [OK] GET /bar [testauth] basic authentication
    [OK] GET /bar [testauth] Broken authorization headers returns a 401
    

.. toctree::
   :maxdepth: 2

   configuration
   default_controllers
   writing_controllers

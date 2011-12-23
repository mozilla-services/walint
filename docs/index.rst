WALint - Web Application Lint
=============================

WALint (Web App Lint) is a tool for testing your web services against a set
of common HTTP metrics. The main goal is to test that your application does not
fail on some weird cases, and that it complies with the HTTP specification.

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


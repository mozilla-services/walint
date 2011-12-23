List of default controllers
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


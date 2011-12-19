import sys

from webtest import TestApp

from walint.util import resolve_name, CatchErrors, default_stream
from walint.config import WalintParser, Controller


def run(app, tests, controllers, services, singles, config,
        stream_result=None):

    def _call_controller(controller, params, method=None, service=None):
        if not isinstance(controller, Controller):
            controller = Controller(controller, params, controller)

        # a controller is setup for each method
        if controller.setup is not None:
            controller.setup(app, config)

        try:
            if not method:
                # it's a single
                args = [app, config]
            else:
                caller = getattr(app, method.lower())
                args = [method, service, app, caller, config]

            # get the params defined in the test, fallback to the ctl
            # definition
            if params:
                args.append(params)
            elif controller.params:
                args.append(controller.params)

            success = controller.func(*args)

            stream_result("[%s] %s" % (test.name, controller.description),
                          getattr(service, 'path', None), method, success)

            return (success, controller.description)

        finally:
            if controller.teardown is not None:
                controller.teardown(app, config)

    # if the `python-path` is specified in the configuration, append the given
    # path to the existing one
    if 'python-path' in config:
        sys.path.append(config['python-path'])

    results = []
    if stream_result is None:
        stream_result = default_stream

    for test_name, test in tests.items():

        # call singles
        for alias, params in test.singles:
            single = singles.get(alias) if alias in singles else alias
            if single:
                results.append(_call_controller(single, params))

        # loop on services / controllers / methods
        for name, methods in test.services:
            service = services.get(name)

            if service.setup is not None:
                service.setup(app, config)

            try:
                for alias, params in test.controllers:
                    controller = controllers.get(alias)

                    # only get the authorized methods
                    for method in set(methods) & set(controller.methods):
                        results.append(
                                _call_controller(controller, params, method,
                                                 service))
            finally:
                if service.teardown is not None:
                    service.teardown()

    return results


def build_app(app):
    if app.startswith('http'):
        raise NotImplementedError()
    return TestApp(CatchErrors(resolve_name(app)))


def main(filename):
    # load the config
    config = WalintParser()
    config.read(filename)

    stream = config.get('walint', 'stream')

    # creating the app client
    app = build_app(config.get('walint', 'root'))

    # now running the tests
    results = run(app, config.get_tests(), config.get_controllers(),
                  config.get_services(), config.get_singles(),
                  config.root_options(), stream)

    return results


def run_cli():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="filename", help="configuration filename")

    args = parser.parse_args()

    results = main(args.filename)

    sys.exit(len(results) != 0)


if __name__ == '__main__':
    run_cli()

import sys

from webtest import TestApp

from walint.util import resolve_name, CatchErrors
from walint.config import WALintParser


def _default_stream(msg, path=None, method=None, success=True):

    OK = '\033[92m'
    FAIL = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

    if path is not None:
        path = BLUE + '%s %s ' % (method, path) + ENDC
    else:
        path = ''

    if success:
        print(OK + '[OK] ' + ENDC + path + msg)
    else:
        print(FAIL + '[KO] ' + ENDC + path + msg)


def run(app, tests, controllers, services, config, stream_result=None):
    # what about global setup.teardown ?
    #
    results = []
    if stream_result is None:
        stream_result = _default_stream

    #for name, single in singles:
    #    success = single(app, config)
    #    msg = _get_function_desc(single, name)
    #    stream_result(msg, None, None, success)
    #    results.append((success, msg))

    for test_name, test in tests.items():
        for name, methods in test.services:
            service = services.get(name)

            for alias, params in test.controllers:
                controller = controllers.get(alias)

                # only get the authorised methods
                for method in set(methods) & set(controller.methods):
                    if service.setup is not None:
                        service.setup(app, config)

                    try:
                        caller = getattr(app, method.lower())
                        args = (method, service, app, caller)

                        if controller.params is not None:
                            args.append(controller.params)

                        success = controller.func(*args)

                        stream_result(test.name + controller.description,
                                        service.path, method, success)
                        results.append((success, controller.description))
                    finally:
                        if service.teardown is not None:
                            service.teardown(app, config)
    return results


def build_app(app):
    if app.startswith('http'):
        raise NotImplementedError()
    return TestApp(CatchErrors(resolve_name(app)))


def main(filename):
    # load the config
    config = WALintParser()
    config.read(filename)

    stream = config.get('walint', 'stream')

    # creating the app client
    app = build_app(config.get('walint', 'root'))

    # getting singles
    # singles = get_singles(config) # XXX fix this

    # now running the tests
    results = run(app, config.tests(), config.controllers(),
                  config.services(), config.root_options(), stream)

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

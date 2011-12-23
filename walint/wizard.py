"""Wizard to create a config file"""
import os
from walint.util import METHS
import sys
from ConfigParser import ConfigParser


OK = '\033[92m'
FAIL = '\033[91m'
BLUE = '\033[94m'
LGRAY = '\033[0;37m'
ENDC = '\033[0m'


def help(msg):
    print(LGRAY + msg + ENDC)


def error(msg):
    print(FAIL + msg + ENDC)


def ask(msg):
    try:
        return raw_input(msg + ' ')
    except KeyboardInterrupt:
        print('')
        error('kthxbye.. :o')
        sys.exit(1)


def ask_yn(msg):
    res = None
    while res is None:
        resp = ask(msg)
        resp = resp.strip().lower()
        if resp in ('y', 'yes'):
            return True
        elif ('n', 'no'):
            return False
        else:
            print("Please answer by 'yes' or 'no' !")


def generate_config(path, root, services):
    cfg = ConfigParser()
    cfg.add_section('walint')
    cfg.set('walint', 'root', root)

    # adding the services
    fservices = []
    for index, (service, options) in enumerate(services.items()):
        name = service.strip('/')
        if name == '':
            name = 'root'
        section = 'service:%s' % name
        cfg.add_section(section)
        cfg.set(section, 'path', service)
        methods = '|'.join(options[0])
        cfg.set(section, 'methods', methods)
        if index > 0:
            space = '    '
        else:
            space = ''
        fservices.append('%s%s %s' % (space, name, methods))

    # adding the main test section
    cfg.add_section('test:all')
    cfg.set('test:all', 'singles', 'walint.singles.check_404')
    cfg.set('test:all', 'controllers', 'walint.singles.json_breaker')
    cfg.set('test:all', 'services', '\n'.join(fservices))

    with open(path, 'w') as f:
        cfg.write(f)

    print('Config generated at %r' % path)


def main(filename):
    if os.path.exists(filename):
        error('%r already exists !' % filename)
        return

    help('Welcome to the WALint wizard')
    print('')

    root = None
    while root is None:
        res = ask("What's the root URL of your application "
                  "(e.g. http://example.com) ?")
        if not res.startswith('http'):
            error("We are just compatible with http apps !"
                  " e.g. 'http://example.com'")
        else:
            root = res.strip()
            if res.endswith('/'):
                res = res[-1]

    print('')
    help("Let's list your services now.")
    help("A service is a path on your server, and some HTTP methods")
    print('')

    services = {}

    while True:
        path = ask("Add a path (like: /users ) [leave empty to stop]")


        if path in services:
            error("Ah, bummer, this one was already defined")
            if not ask_yn("Do you want to override it ?"):
                help("Ok -- keeping the old one")
                continue

        if path == '':
            break

        if not path.startswith('/'):
            path = '/' + path

        if len(path) > 1 and path[-1] == '/':
            path = path[:-1]

        print('')
        help('Methods we support are %s.' % ', '.join(METHS))
        help('You can separate them by a pipe ("|").')
        print('')

        qu = ('What HTTP methods do you support on "%s" (like GET or POST) ?'\
                % path)

        methods = None

        while methods is None:
            meths = ask(qu)

            meths = [meth.strip().upper()
                        for meth in meths.strip().split('|')
                     if meth.strip() != '']

            for meth in meths:
                if meth not in METHS:
                    error("Ah, bummer, %s is not supported" % meth)
                    break
            else:
                methods = meths

        if 'POST' in methods or 'PUT' in methods:
            qu = 'Oh, I see you have a PUT or POST there, do you expect json ?'
            if ask_yn(qu):
                help("Walint will do a few extra json tests ;)")
                json = True
            else:
                json = False

        help('Ok. %s %s was added.' % (path, '|'.join(methods)))
        services[path] = (methods, json)
        print('')

    generate_config(filename, root, services)

    print('')
    print("To run the test, just call 'walint' against this config file")
    help('Thank you!')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        error("C'mon. We need a path for the config file to create.")
        sys.exit(1)

    main(sys.argv[1])

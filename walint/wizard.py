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
        res = ask("What's the root URL of your application ?")
        if not res.startswith('http'):
            error("We are just compatible with http apps !"
                  " e.g. 'http://example.com'")
        else:
            root = res.strip()
            if res.endswith('/'):
                res = res[-1]

    print('')
    help("Let's list your services now.")
    help("A service is a path on your server, and HTTP methods")
    print('')

    services = {}

    while True:
        path = ask("Add a path [leave empty to stop]")


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

        qu = ('What HTTP methods do you support on "%s" ?' % path)

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


        help('Ok. %s %s was added.' % (path, '|'.join(methods)))
        services[path] = (methods,)
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


""" Default controllers
"""
from webtest.app import AppError

from walint.util import METHS, random_path
from walint import logger


def _err(caller, path, status):
    try:
        caller(path, status=status)
    except AppError, res:
        logger.error(str(res))
        # XXX
        print(res)
        return False
    return True

def check_404(app):
    """Makes sure non-existant paths return a 404"""
    path  = random_path()
    for meth in METHS:
        caller = getattr(app, meth.lower())
        if not _err(caller, path, 404):
            return False
    return True


def check_414(method, path, app, caller):
    """Checks that uri > 4096 generates a 414"""
    path = path + '?' + 'o' * 5000 + '=1'
    return _err(caller, path, status=414)

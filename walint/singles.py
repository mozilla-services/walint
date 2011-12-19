from walint.util import METHS, random_path, _err


def check_404(app, config, services, *params):
    """Makes sure non-existant paths return a 404"""
    path = random_path()
    for meth in METHS:
        caller = getattr(app, meth.lower())
        if not _err(caller, path, status=404):
            return False
    return True

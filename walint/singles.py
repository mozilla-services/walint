from walint.util import METHS, random_path, _err


def check_404(app, config, services, *params):
    """Non-existant paths return a 404"""
    path = random_path()
    for meth in METHS:
        caller = getattr(app, meth.lower())
        if not _err(caller, path, status=404):
            return False
    return True


def check_405(app, config, services, *params):
    """Wrong HTTP method on a right URI returns a 405"""
    #  from the list of services, get one with not all methods defined
    for service in services.values():
        diff = set(METHS) - set(service.methods)
        if diff:
            return _err(getattr(app, diff.pop().lower()),
                        service.path, status=405)

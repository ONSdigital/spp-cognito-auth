from functools import wraps
from flask import current_app, redirect


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_app.auth.logged_in():
            return f(*args, **kwargs)
        return redirect(current_app.auth.login_url())

    return decorated

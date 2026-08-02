from flask import session, redirect, url_for
from functools import wraps

def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorador
from functools import wraps
from flask import session, redirect, flash


def login_required(f):
    """Protege rutas: solo usuarios autenticados."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder.", "error")
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper

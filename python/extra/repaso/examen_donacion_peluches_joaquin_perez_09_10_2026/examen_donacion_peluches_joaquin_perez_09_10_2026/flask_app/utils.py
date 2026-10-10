from functools import wraps

from flask import flash, redirect, session


def login_requerido(vista):
    """Redirige al inicio si el usuario no ha iniciado sesión."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para ver esta página.", "login")
            return redirect("/")
        return vista(*args, **kwargs)
    return envoltura




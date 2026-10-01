from functools import wraps

from flask import flash, redirect, render_template, request, session

from flask_app import app
from flask_app.models.user import User


def login_required(view):
    """Protege rutas: exige usuario autenticado en sesión."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder.", "login")
            return redirect("/")
        return view(*args, **kwargs)
    return wrapper


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/libros")
    return render_template("index.html")


@app.route("/registro", methods=["POST"])
def register():
    if not User.validate_register(request.form):
        return redirect("/")
    user_id = User.create({
        "first_name": request.form["first_name"].strip(),
        "last_name": request.form["last_name"].strip(),
        "email": request.form["email"].strip(),
        "password": User.hash_password(request.form["password"]),
    })
    if not user_id:
        flash("No se pudo crear la cuenta. Intenta nuevamente.", "register")
        return redirect("/")
    session["user_id"] = user_id
    session["first_name"] = request.form["first_name"].strip()
    flash("¡Cuenta creada con éxito!", "success")
    return redirect("/libros")


@app.route("/login", methods=["POST"])
def login():
    user = User.get_by_email(request.form.get("email", "").strip())
    if not user or not User.check_password(user.password, request.form.get("password", "")):
        flash("E-mail o contraseña incorrectos.", "login")
        return redirect("/")
    session["user_id"] = user.id
    session["first_name"] = user.first_name
    return redirect("/libros")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

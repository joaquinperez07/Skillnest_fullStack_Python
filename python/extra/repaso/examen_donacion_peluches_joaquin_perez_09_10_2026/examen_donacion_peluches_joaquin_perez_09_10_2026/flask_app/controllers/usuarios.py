from flask import flash, redirect, render_template, request, session
from flask_bcrypt import Bcrypt

from flask_app import app
from flask_app.models.usuario import Usuario

bcrypt = Bcrypt(app)


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect("/dashboard")
    return render_template("index.html")


@app.route("/registro", methods=["POST"])
def registro():
    if not Usuario.validar_registro(request.form):
        return redirect("/")

    data = {
        "nombre": request.form["nombre"].strip(),
        "apellido": request.form["apellido"].strip(),
        "email": request.form["email"].strip(),
        "password": bcrypt.generate_password_hash(request.form["password"]),
    }
    usuario_id = Usuario.crear(data)
    if not usuario_id:
        flash("No se pudo completar el registro.", "registro")
        return redirect("/")

    session["usuario_id"] = usuario_id
    session["nombre"] = data["nombre"]
    return redirect("/dashboard")


@app.route("/login", methods=["POST"])
def login():
    usuario = Usuario.obtener_por_email(request.form["email"].strip())
    password = request.form["password"]

    if (
        not usuario
        or len(password.encode("utf-8")) > 72
        or not bcrypt.check_password_hash(usuario.password, password)
    ):
        flash("Email o contraseña incorrectos.", "login")
        return redirect("/")

    session["usuario_id"] = usuario.id
    session["nombre"] = usuario.nombre
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

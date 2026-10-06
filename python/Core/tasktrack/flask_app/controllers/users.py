from flask import render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from flask_app import app
from flask_app.models.user import User
from flask_app.models.task import Task
from flask_app.utils import login_required

bcrypt = Bcrypt(app)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("index.html", form=session.pop("form", {}))


@app.route("/register", methods=["POST"])
def register():
    if not User.validate_register(request.form):
        session["form"] = {"first_name": request.form.get("first_name", ""),
                           "last_name": request.form.get("last_name", ""),
                           "email": request.form.get("email", "")}
        return redirect("/")
    user_id = User.create({
        "first_name": request.form["first_name"].strip(),
        "last_name": request.form["last_name"].strip(),
        "email": request.form["email"].strip().lower(),
        "password": bcrypt.generate_password_hash(request.form["password"]).decode("utf-8"),
    })
    if not user_id:
        flash("No se pudo crear la cuenta. Intenta nuevamente.", "error")
        return redirect("/")
    session["user_id"] = user_id
    session["first_name"] = request.form["first_name"].strip()
    flash("¡Cuenta creada con éxito! Bienvenido/a a TaskTrack.", "success")
    return redirect("/dashboard")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("login_email", "").strip().lower()
    password = request.form.get("login_password", "")
    user = User.get_by_email(email)
    # Mismo mensaje para email inexistente y contraseña incorrecta
    if not user or not bcrypt.check_password_hash(user.password, password):
        flash("Email o contraseña incorrectos.", "login_error")
        return redirect("/")
    session["user_id"] = user.id
    session["first_name"] = user.first_name
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    status = request.args.get("status", "")
    search = request.args.get("q", "").strip()
    return render_template(
        "dashboard.html",
        tasks=Task.get_all_by_user(uid, status or None, search or None),
        upcoming=Task.upcoming(uid),
        summary=Task.summary(uid),
        status=status, search=search,
    )


@app.route("/perfil")
@login_required
def perfil():
    uid = session["user_id"]
    return render_template("perfil.html", user=User.get_by_id(uid), summary=Task.summary(uid))

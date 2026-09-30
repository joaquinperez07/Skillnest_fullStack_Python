import re
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, session
from flask_bcrypt import Bcrypt

from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = "cambia-esta-clave-secreta"
bcrypt = Bcrypt(app)

DB = "login_registro_db"
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
GENEROS = ["Femenino", "Masculino", "Otro", "Prefiero no decirlo"]


# ---------- Utilidades ----------
def get_user_by_email(email):
    result = connectToMySQL(DB).query_db(
        "SELECT * FROM users WHERE email = %(email)s;", {"email": email}
    )
    return result[0] if result else None


def get_user_by_id(user_id):
    result = connectToMySQL(DB).query_db(
        "SELECT * FROM users WHERE id = %(id)s;", {"id": user_id}
    )
    return result[0] if result else None


def calcular_edad(nacimiento):
    hoy = date.today()
    return hoy.year - nacimiento.year - (
        (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
    )


def validar_registro(form):
    valido = True
    nombre = form.get("first_name", "").strip()
    apellido = form.get("last_name", "").strip()
    email = form.get("email", "").strip().lower()
    password = form.get("password", "")
    confirm = form.get("confirm_password", "")
    nacimiento = form.get("birth_date", "")
    genero = form.get("gender", "")

    # Nombre
    if not nombre:
        flash("El nombre no puede estar vacío.", "registro")
        valido = False
    elif len(nombre) < 2 or not nombre.replace(" ", "").isalpha():
        flash("El nombre debe tener al menos 2 letras y solo contener letras.", "registro")
        valido = False

    # Apellido
    if not apellido:
        flash("El apellido no puede estar vacío.", "registro")
        valido = False
    elif len(apellido) < 2 or not apellido.replace(" ", "").isalpha():
        flash("El apellido debe tener al menos 2 letras y solo contener letras.", "registro")
        valido = False

    # E-mail
    if not email:
        flash("El e-mail no puede estar vacío.", "registro")
        valido = False
    elif not EMAIL_REGEX.match(email):
        flash("El formato del e-mail no es válido.", "registro")
        valido = False
    elif get_user_by_email(email):
        flash("Ese e-mail ya está registrado.", "registro")
        valido = False

    # Contraseña (incluye BONUS DE PLATA: número y mayúscula)
    if not password:
        flash("La contraseña no puede estar vacía.", "registro")
        valido = False
    else:
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "registro")
            valido = False
        if not re.search(r"\d", password):
            flash("La contraseña debe incluir al menos un número.", "registro")
            valido = False
        if not re.search(r"[A-Z]", password):
            flash("La contraseña debe incluir al menos una mayúscula.", "registro")
            valido = False

    # Confirmación
    if password != confirm:
        flash("La confirmación no coincide con la contraseña.", "registro")
        valido = False

    # BONUS DE ORO: fecha de nacimiento (mayor de edad), género, términos
    if not nacimiento:
        flash("La fecha de nacimiento es obligatoria.", "registro")
        valido = False
    else:
        try:
            fecha = datetime.strptime(nacimiento, "%Y-%m-%d").date()
            if fecha > date.today():
                flash("La fecha de nacimiento no puede estar en el futuro.", "registro")
                valido = False
            elif calcular_edad(fecha) < 18:
                flash("Debes ser mayor de edad (18+) para registrarte.", "registro")
                valido = False
        except ValueError:
            flash("La fecha de nacimiento no es válida.", "registro")
            valido = False

    if genero not in GENEROS:
        flash("Selecciona una opción de género válida.", "registro")
        valido = False

    if not form.get("terms"):
        flash("Debes aceptar los términos y condiciones.", "registro")
        valido = False

    return valido


# ---------- Rutas ----------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/exito")
    return render_template("index.html", generos=GENEROS)


@app.route("/registrar", methods=["POST"])
def registrar():
    if not validar_registro(request.form):
        return redirect("/")

    pw_hash = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
    data = {
        "first_name": request.form["first_name"].strip().title(),
        "last_name": request.form["last_name"].strip().title(),
        "email": request.form["email"].strip().lower(),
        "birth_date": request.form["birth_date"],
        "gender": request.form["gender"],
        "password": pw_hash,
    }
    query = """INSERT INTO users (first_name, last_name, email, birth_date, gender, password)
               VALUES (%(first_name)s, %(last_name)s, %(email)s, %(birth_date)s,
                       %(gender)s, %(password)s);"""
    user_id = connectToMySQL(DB).query_db(query, data)
    if not user_id:
        flash("No se pudo guardar el registro. Inténtalo de nuevo.", "registro")
        return redirect("/")

    session["user_id"] = user_id
    return redirect("/exito")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email) if email else None
    # Mensaje genérico para no revelar si el correo existe
    if not user or not bcrypt.check_password_hash(user["password"], password):
        flash("E-mail o contraseña incorrectos.", "login")
        return redirect("/")

    session["user_id"] = user["id"]
    return redirect("/exito")


@app.route("/exito")
def exito():
    if "user_id" not in session:
        flash("Debes iniciar sesión para ver esa página.", "login")
        return redirect("/")
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return redirect("/")
    return render_template("exito.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.after_request
def no_cache(response):
    # Evita que el botón "atrás" muestre páginas protegidas tras cerrar sesión
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


if __name__ == "__main__":
    app.run(debug=True)

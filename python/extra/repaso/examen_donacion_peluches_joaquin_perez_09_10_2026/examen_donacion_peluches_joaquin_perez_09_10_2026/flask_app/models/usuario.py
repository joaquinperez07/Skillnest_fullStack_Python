import re

from flask import flash

from flask_app.config.mysql_connection import connect_to_mysql

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")


class Usuario:
    def __init__(self, data):
        self.id = data["id"]
        self.nombre = data["nombre"]
        self.apellido = data["apellido"]
        self.email = data.get("email")
        self.password = data.get("password")

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO usuarios (nombre, apellido, email, password)
            VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s);
        """
        return connect_to_mysql().query_db(query, data)

    @classmethod
    def obtener_por_email(cls, email):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connect_to_mysql().query_db(query, {"email": email})
        return cls(resultado[0]) if resultado else None

    @staticmethod
    def validar_registro(form):
        valido = True
        if len(form["nombre"].strip()) < 2:
            flash("El nombre debe tener al menos 2 caracteres.", "registro")
            valido = False
        if len(form["apellido"].strip()) < 2:
            flash("El apellido debe tener al menos 2 caracteres.", "registro")
            valido = False
        email = form["email"].strip()
        if not EMAIL_REGEX.match(email):
            flash("El formato del email no es válido.", "registro")
            valido = False
        elif Usuario.obtener_por_email(email):
            flash("Ese email ya está registrado.", "registro")
            valido = False
        if len(form["password"]) == 0:
            flash("La contraseña no puede estar vacía.", "registro")
            valido = False
        elif len(form["password"].encode("utf-8")) > 72:
            flash("La contraseña es demasiado larga (máximo 72 bytes).", "registro")
            valido = False
        elif form["password"] != form["confirmar_password"]:
            flash("La contraseña y su confirmación deben ser iguales.", "registro")
            valido = False
        return valido

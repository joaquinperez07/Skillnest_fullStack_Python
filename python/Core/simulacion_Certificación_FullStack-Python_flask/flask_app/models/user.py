import re

from flask import flash

from flask_app import DATABASE, bcrypt
from flask_app.config.mysqlconnection import connectToMySQL

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")


class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data.get("password")

    # ---------- Consultas ----------
    @classmethod
    def get_by_email(cls, email):
        rows = connectToMySQL(DATABASE).query_db(
            "SELECT * FROM users WHERE email = %(email)s;", {"email": email}
        )
        return cls(rows[0]) if rows else None

    @classmethod
    def get_by_id(cls, user_id):
        rows = connectToMySQL(DATABASE).query_db(
            "SELECT * FROM users WHERE id = %(id)s;", {"id": user_id}
        )
        return cls(rows[0]) if rows else None

    @classmethod
    def create(cls, data):
        query = """INSERT INTO users (first_name, last_name, email, password)
                   VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"""
        return connectToMySQL(DATABASE).query_db(query, data)

    # ---------- Validaciones ----------
    @staticmethod
    def validate_register(form):
        is_valid = True
        if len(form.get("first_name", "").strip()) < 2:
            flash("El nombre debe tener al menos 2 caracteres.", "register")
            is_valid = False
        if len(form.get("last_name", "").strip()) < 2:
            flash("El apellido debe tener al menos 2 caracteres.", "register")
            is_valid = False
        email = form.get("email", "").strip()
        if not EMAIL_REGEX.match(email):
            flash("Ingresa un e-mail con formato válido.", "register")
            is_valid = False
        elif User.get_by_email(email):
            flash("Ese e-mail ya está registrado.", "register")
            is_valid = False
        if len(form.get("password", "")) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "register")
            is_valid = False
        if form.get("password", "") != form.get("confirm_password", ""):
            flash("La contraseña y su confirmación deben ser iguales.", "register")
            is_valid = False
        return is_valid

    @staticmethod
    def hash_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @staticmethod
    def check_password(hashed, password):
        return bcrypt.check_password_hash(hashed, password)

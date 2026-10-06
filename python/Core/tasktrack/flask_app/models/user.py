import re
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")


class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data.get("created_at")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def create(cls, data):
        q = """INSERT INTO users (first_name, last_name, email, password)
               VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);"""
        return connectToMySQL().query_db(q, data)

    @classmethod
    def get_by_email(cls, email):
        rows = connectToMySQL().query_db("SELECT * FROM users WHERE email = %(email)s;", {"email": email})
        return cls(rows[0]) if rows else None

    @classmethod
    def get_by_id(cls, user_id):
        rows = connectToMySQL().query_db("SELECT * FROM users WHERE id = %(id)s;", {"id": user_id})
        return cls(rows[0]) if rows else None

    @staticmethod
    def validate_register(form):
        ok = True
        if len(form.get("first_name", "").strip()) < 2:
            flash("El nombre debe tener al menos 2 caracteres.", "error"); ok = False
        if len(form.get("last_name", "").strip()) < 2:
            flash("El apellido debe tener al menos 2 caracteres.", "error"); ok = False
        email = form.get("email", "").strip().lower()
        if not EMAIL_REGEX.match(email):
            flash("El email no tiene un formato válido.", "error"); ok = False
        elif User.get_by_email(email):
            flash("Ese email ya está registrado.", "error"); ok = False
        if len(form.get("password", "")) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error"); ok = False
        if form.get("password", "") != form.get("confirm_password", ""):
            flash("La contraseña y su confirmación no coinciden.", "error"); ok = False
        return ok

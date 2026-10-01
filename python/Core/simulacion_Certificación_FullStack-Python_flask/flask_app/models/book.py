from datetime import date, datetime

from flask import flash

from flask_app import DATABASE
from flask_app.config.mysqlconnection import connectToMySQL

GENRES = [
    "Novela", "Fábula", "Ciencia Ficción", "Fantasía", "Romance", "Misterio",
    "Historia", "Poesía", "Desarrollo Personal", "Otro",
]


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class Book:
    # ---------- Consultas ----------
    @classmethod
    def get_by_user(cls, user_id):
        """Libros publicados por el usuario, con cantidad de favoritos."""
        query = """
            SELECT b.*, COUNT(f.user_id) AS favorites_count
            FROM books b
            LEFT JOIN favorites f ON f.book_id = b.id
            WHERE b.user_id = %(user_id)s
            GROUP BY b.id
            ORDER BY b.created_at DESC;"""
        return connectToMySQL(DATABASE).query_db(query, {"user_id": user_id}) or []

    @classmethod
    def get_community(cls, user_id):
        """Libros publicados por los demás usuarios."""
        query = """
            SELECT b.*, u.first_name AS publisher, COUNT(f.user_id) AS favorites_count
            FROM books b
            JOIN users u ON u.id = b.user_id
            LEFT JOIN favorites f ON f.book_id = b.id
            WHERE b.user_id <> %(user_id)s
            GROUP BY b.id, u.first_name
            ORDER BY b.created_at DESC;"""
        return connectToMySQL(DATABASE).query_db(query, {"user_id": user_id}) or []

    @classmethod
    def get_all(cls):
        query = """
            SELECT b.*, u.first_name AS publisher, COUNT(f.user_id) AS favorites_count
            FROM books b
            JOIN users u ON u.id = b.user_id
            LEFT JOIN favorites f ON f.book_id = b.id
            GROUP BY b.id, u.first_name
            ORDER BY b.created_at DESC;"""
        return connectToMySQL(DATABASE).query_db(query) or []

    @classmethod
    def get_one(cls, book_id):
        query = """
            SELECT b.*, u.first_name AS publisher
            FROM books b
            JOIN users u ON u.id = b.user_id
            WHERE b.id = %(id)s;"""
        rows = connectToMySQL(DATABASE).query_db(query, {"id": book_id})
        return rows[0] if rows else None

    @classmethod
    def get_favorited_by(cls, book_id):
        """Usuarios que agregaron el libro a favoritos."""
        query = """
            SELECT u.id, u.first_name, u.last_name
            FROM favorites f
            JOIN users u ON u.id = f.user_id
            WHERE f.book_id = %(id)s
            ORDER BY f.created_at;"""
        return connectToMySQL(DATABASE).query_db(query, {"id": book_id}) or []

    @classmethod
    def get_favorites_of_user(cls, user_id):
        query = """
            SELECT b.*
            FROM favorites f
            JOIN books b ON b.id = f.book_id
            WHERE f.user_id = %(user_id)s
            ORDER BY f.created_at DESC;"""
        return connectToMySQL(DATABASE).query_db(query, {"user_id": user_id}) or []

    # ---------- Escritura ----------
    @classmethod
    def create(cls, data):
        query = """INSERT INTO books (title, author, genre, publication_date, description, user_id)
                   VALUES (%(title)s, %(author)s, %(genre)s, %(publication_date)s,
                           %(description)s, %(user_id)s);"""
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def update(cls, data):
        query = """UPDATE books
                   SET title = %(title)s, author = %(author)s, genre = %(genre)s,
                       publication_date = %(publication_date)s, description = %(description)s
                   WHERE id = %(id)s AND user_id = %(user_id)s;"""
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def delete(cls, book_id, user_id):
        # La condición user_id garantiza que solo el dueño pueda borrar.
        query = "DELETE FROM books WHERE id = %(id)s AND user_id = %(user_id)s;"
        return connectToMySQL(DATABASE).query_db(query, {"id": book_id, "user_id": user_id})

    # ---------- Favoritos ----------
    @classmethod
    def is_favorite(cls, user_id, book_id):
        rows = connectToMySQL(DATABASE).query_db(
            "SELECT 1 FROM favorites WHERE user_id = %(u)s AND book_id = %(b)s;",
            {"u": user_id, "b": book_id},
        )
        return bool(rows)

    @classmethod
    def add_favorite(cls, user_id, book_id):
        return connectToMySQL(DATABASE).query_db(
            "INSERT IGNORE INTO favorites (user_id, book_id) VALUES (%(u)s, %(b)s);",
            {"u": user_id, "b": book_id},
        )

    # ---------- Validaciones ----------
    @staticmethod
    def validate(form, original_date=None):
        """original_date: fecha ya guardada (en edición se permite conservarla)."""
        is_valid = True
        if len(form.get("title", "").strip()) < 2:
            flash("El título debe tener al menos 2 caracteres.", "book")
            is_valid = False
        if not form.get("author", "").strip():
            flash("El autor es obligatorio.", "book")
            is_valid = False
        if form.get("genre", "") not in GENRES:
            flash("Debes seleccionar un género.", "book")
            is_valid = False

        pub_date = _parse_date(form.get("publication_date"))
        if pub_date is None:
            flash("La fecha de publicación es obligatoria.", "book")
            is_valid = False
        elif pub_date < date.today() and pub_date != original_date:
            flash("La fecha de publicación no puede ser pasada.", "book")
            is_valid = False

        if len(form.get("description", "").strip()) < 10:
            flash("La descripción debe tener al menos 10 caracteres.", "book")
            is_valid = False
        return is_valid

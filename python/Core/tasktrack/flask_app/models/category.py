from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL


class Category:
    @classmethod
    def get_all_by_user(cls, user_id):
        """Categorías del usuario con el total de tareas de cada una (LEFT JOIN + COUNT)."""
        q = """SELECT c.id, c.name, COUNT(t.id) AS total_tasks
               FROM categories c
               LEFT JOIN tasks t ON t.category_id = c.id
               WHERE c.user_id = %(user_id)s
               GROUP BY c.id, c.name
               ORDER BY c.name;"""
        return connectToMySQL().query_db(q, {"user_id": user_id}) or []

    @classmethod
    def get_one(cls, category_id, user_id):
        """Devuelve la categoría solo si pertenece al usuario."""
        q = "SELECT * FROM categories WHERE id = %(id)s AND user_id = %(user_id)s;"
        rows = connectToMySQL().query_db(q, {"id": category_id, "user_id": user_id})
        return rows[0] if rows else None

    @classmethod
    def create(cls, data):
        return connectToMySQL().query_db(
            "INSERT INTO categories (name, user_id) VALUES (%(name)s, %(user_id)s);", data)

    @classmethod
    def update(cls, data):
        return connectToMySQL().query_db(
            "UPDATE categories SET name = %(name)s WHERE id = %(id)s AND user_id = %(user_id)s;", data)

    @classmethod
    def delete(cls, category_id, user_id):
        return connectToMySQL().query_db(
            "DELETE FROM categories WHERE id = %(id)s AND user_id = %(user_id)s;",
            {"id": category_id, "user_id": user_id})

    @classmethod
    def count_tasks(cls, category_id):
        rows = connectToMySQL().query_db(
            "SELECT COUNT(*) AS n FROM tasks WHERE category_id = %(id)s;", {"id": category_id})
        return rows[0]["n"] if rows else 0

    @staticmethod
    def validate(form, user_id, exclude_id=None):
        name = form.get("name", "").strip()
        if len(name) < 3:
            flash("El nombre de la categoría debe tener al menos 3 caracteres.", "error")
            return False
        if len(name) > 100:
            flash("El nombre de la categoría es demasiado largo (máx. 100).", "error")
            return False
        rows = connectToMySQL().query_db(
            "SELECT id FROM categories WHERE user_id = %(u)s AND LOWER(name) = LOWER(%(n)s);",
            {"u": user_id, "n": name}) or []
        if any(r["id"] != exclude_id for r in rows):
            flash("Ya tienes una categoría con ese nombre.", "error")
            return False
        return True

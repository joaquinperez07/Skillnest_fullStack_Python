from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL


class Comment:
    @classmethod
    def get_by_task(cls, task_id):
        q = """SELECT cm.*, CONCAT(u.first_name, ' ', u.last_name) AS author
               FROM comments cm JOIN users u ON u.id = cm.user_id
               WHERE cm.task_id = %(t)s ORDER BY cm.created_at DESC, cm.id DESC;"""
        return connectToMySQL().query_db(q, {"t": task_id}) or []

    @classmethod
    def create(cls, data):
        return connectToMySQL().query_db(
            "INSERT INTO comments (content, task_id, user_id) VALUES (%(content)s, %(task_id)s, %(user_id)s);",
            data)

    @classmethod
    def get_one(cls, comment_id):
        rows = connectToMySQL().query_db("SELECT * FROM comments WHERE id = %(id)s;", {"id": comment_id})
        return rows[0] if rows else None

    @classmethod
    def delete(cls, comment_id, user_id):
        """Solo el autor del comentario puede borrarlo."""
        return connectToMySQL().query_db(
            "DELETE FROM comments WHERE id = %(id)s AND user_id = %(u)s;", {"id": comment_id, "u": user_id})

    @staticmethod
    def validate(form):
        text = form.get("content", "").strip()
        if len(text) < 2:
            flash("El comentario debe tener al menos 2 caracteres.", "error"); return False
        if len(text) > 500:
            flash("El comentario no puede superar los 500 caracteres.", "error"); return False
        return True

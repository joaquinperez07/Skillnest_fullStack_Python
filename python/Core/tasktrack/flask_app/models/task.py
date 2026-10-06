from datetime import date, datetime
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.category import Category

PRIORITIES = ["Alta", "Media", "Baja"]
STATUSES = ["Pendiente", "En progreso", "Completada"]


class Task:
    # ---------- CREATE ----------
    @classmethod
    def create(cls, data):
        q = """INSERT INTO tasks (title, description, priority, status, due_date, user_id, category_id)
               VALUES (%(title)s, %(description)s, %(priority)s, 'Pendiente', %(due_date)s,
                       %(user_id)s, %(category_id)s);"""
        return connectToMySQL().query_db(q, data)

    # ---------- READ ----------
    @classmethod
    def get_all_by_user(cls, user_id, status=None, search=None):
        """Tareas del usuario con su categoría (JOIN), ordenadas por fecha más cercana.
        Soporta filtro por estado y búsqueda por título."""
        q = """SELECT t.*, c.name AS category_name
               FROM tasks t JOIN categories c ON c.id = t.category_id
               WHERE t.user_id = %(user_id)s"""
        data = {"user_id": user_id}
        if status in STATUSES:
            q += " AND t.status = %(status)s"; data["status"] = status
        if search:
            q += " AND t.title LIKE %(search)s"; data["search"] = f"%{search}%"
        q += " ORDER BY t.due_date ASC, t.id ASC;"
        return connectToMySQL().query_db(q, data) or []

    @classmethod
    def get_by_category(cls, user_id, category_id):
        q = """SELECT t.*, c.name AS category_name
               FROM tasks t JOIN categories c ON c.id = t.category_id
               WHERE t.user_id = %(u)s AND t.category_id = %(c)s ORDER BY t.due_date ASC;"""
        return connectToMySQL().query_db(q, {"u": user_id, "c": category_id}) or []

    @classmethod
    def get_one(cls, task_id, user_id):
        """Tarea con categoría y creador. Solo si pertenece al usuario autenticado."""
        q = """SELECT t.*, c.name AS category_name,
                      CONCAT(u.first_name, ' ', u.last_name) AS creator
               FROM tasks t
               JOIN categories c ON c.id = t.category_id
               JOIN users u ON u.id = t.user_id
               WHERE t.id = %(id)s AND t.user_id = %(user_id)s;"""
        rows = connectToMySQL().query_db(q, {"id": task_id, "user_id": user_id})
        return rows[0] if rows else None

    @classmethod
    def upcoming(cls, user_id, limit=5):
        """Próximas tareas no completadas con los días restantes."""
        q = """SELECT title, due_date, DATEDIFF(due_date, CURDATE()) AS days_left
               FROM tasks
               WHERE user_id = %(u)s AND status <> 'Completada' AND due_date >= CURDATE()
               ORDER BY due_date ASC LIMIT %(l)s;"""
        return connectToMySQL().query_db(q, {"u": user_id, "l": limit}) or []

    @classmethod
    def summary(cls, user_id):
        q = """SELECT COUNT(*) AS total,
                      COALESCE(SUM(status = 'Pendiente'), 0)   AS pendientes,
                      COALESCE(SUM(status = 'En progreso'), 0) AS en_progreso,
                      COALESCE(SUM(status = 'Completada'), 0)  AS completadas,
                      COALESCE(SUM(priority = 'Alta'), 0)  AS alta,
                      COALESCE(SUM(priority = 'Media'), 0) AS media,
                      COALESCE(SUM(priority = 'Baja'), 0)  AS baja
               FROM tasks WHERE user_id = %(u)s;"""
        rows = connectToMySQL().query_db(q, {"u": user_id})
        return rows[0] if rows else {}

    # ---------- UPDATE ----------
    @classmethod
    def update(cls, data):
        q = """UPDATE tasks SET title=%(title)s, description=%(description)s, priority=%(priority)s,
                      status=%(status)s, due_date=%(due_date)s, category_id=%(category_id)s
               WHERE id=%(id)s AND user_id=%(user_id)s;"""
        return connectToMySQL().query_db(q, data)

    @classmethod
    def set_status(cls, task_id, user_id, status):
        q = "UPDATE tasks SET status=%(s)s WHERE id=%(id)s AND user_id=%(u)s;"
        return connectToMySQL().query_db(q, {"s": status, "id": task_id, "u": user_id})

    # ---------- DELETE ----------
    @classmethod
    def delete(cls, task_id, user_id):
        return connectToMySQL().query_db(
            "DELETE FROM tasks WHERE id=%(id)s AND user_id=%(u)s;", {"id": task_id, "u": user_id})

    # ---------- VALIDACIONES ----------
    @staticmethod
    def validate(form, user_id, is_update=False):
        ok = True
        if len(form.get("title", "").strip()) < 3:
            flash("El título debe tener al menos 3 caracteres.", "error"); ok = False
        elif len(form["title"].strip()) > 150:
            flash("El título no puede superar los 150 caracteres.", "error"); ok = False

        cat = form.get("category_id", "")
        if not cat:
            flash("Debes seleccionar una categoría.", "error"); ok = False
        elif not cat.isdigit() or not Category.get_one(int(cat), user_id):
            flash("La categoría seleccionada no es válida.", "error"); ok = False

        if form.get("priority") not in PRIORITIES:
            flash("Debes seleccionar una prioridad.", "error"); ok = False

        if is_update and form.get("status") not in STATUSES:
            flash("El estado seleccionado no es válido.", "error"); ok = False

        raw = form.get("due_date", "")
        if not raw:
            flash("La fecha límite es obligatoria.", "error"); ok = False
        else:
            try:
                d = datetime.strptime(raw, "%Y-%m-%d").date()
                if d < date.today() and not form.get("keep_date") == d.isoformat():
                    flash("La fecha límite no puede ser una fecha pasada.", "error"); ok = False
            except ValueError:
                flash("La fecha límite no tiene un formato válido.", "error"); ok = False

        if len(form.get("description", "").strip()) < 10:
            flash("La descripción debe tener al menos 10 caracteres.", "error"); ok = False
        return ok

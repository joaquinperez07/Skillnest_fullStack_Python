from flask import render_template, request, redirect, session, flash
from flask_app import app
from flask_app.models.task import Task, PRIORITIES, STATUSES
from flask_app.models.category import Category
from flask_app.models.comment import Comment
from flask_app.utils import login_required


def _own_task_or_redirect(task_id):
    task = Task.get_one(task_id, session["user_id"])
    if not task:
        flash("La tarea no existe o no tienes permiso para acceder a ella.", "error")
    return task


@app.route("/tareas/nueva")
@login_required
def new_task():
    return render_template("task_form.html", task=None, form=session.pop("form", {}),
                           categories=Category.get_all_by_user(session["user_id"]),
                           priorities=PRIORITIES, statuses=STATUSES)


@app.route("/tareas/crear", methods=["POST"])
@login_required
def create_task():
    uid = session["user_id"]
    if not Task.validate(request.form, uid):
        session["form"] = request.form.to_dict()
        return redirect("/tareas/nueva")
    Task.create({
        "title": request.form["title"].strip(),
        "description": request.form["description"].strip(),
        "priority": request.form["priority"],
        "due_date": request.form["due_date"],
        "category_id": int(request.form["category_id"]),
        "user_id": uid,
    })
    flash("Tarea creada correctamente.", "success")
    return redirect("/dashboard")


@app.route("/tareas/<int:task_id>")
@login_required
def show_task(task_id):
    task = _own_task_or_redirect(task_id)
    if not task:
        return redirect("/dashboard")
    return render_template("task_detail.html", task=task, comments=Comment.get_by_task(task_id))


@app.route("/tareas/editar/<int:task_id>")
@login_required
def edit_task(task_id):
    task = _own_task_or_redirect(task_id)
    if not task:
        return redirect("/dashboard")
    return render_template("task_form.html", task=task, form=session.pop("form", {}),
                           categories=Category.get_all_by_user(session["user_id"]),
                           priorities=PRIORITIES, statuses=STATUSES)


@app.route("/tareas/actualizar/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    uid = session["user_id"]
    task = _own_task_or_redirect(task_id)
    if not task:
        return redirect("/dashboard")
    form = request.form.to_dict()
    form["keep_date"] = task["due_date"].isoformat()  # permite conservar una fecha ya vencida sin cambios
    if form.get("due_date") != form["keep_date"]:
        form["keep_date"] = ""
    if not Task.validate(form, uid, is_update=True):
        session["form"] = request.form.to_dict()
        return redirect(f"/tareas/editar/{task_id}")
    Task.update({
        "id": task_id, "user_id": uid,
        "title": form["title"].strip(),
        "description": form["description"].strip(),
        "priority": form["priority"],
        "status": form["status"],
        "due_date": form["due_date"],
        "category_id": int(form["category_id"]),
    })
    flash("Tarea actualizada correctamente.", "success")
    return redirect(f"/tareas/{task_id}")


@app.route("/tareas/completar/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    if not _own_task_or_redirect(task_id):
        return redirect("/dashboard")
    Task.set_status(task_id, session["user_id"], "Completada")
    flash("Tarea marcada como completada.", "success")
    return redirect(request.referrer or "/dashboard")


@app.route("/tareas/borrar/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    if not _own_task_or_redirect(task_id):
        return redirect("/dashboard")
    Task.delete(task_id, session["user_id"])
    flash("Tarea eliminada.", "success")
    return redirect("/dashboard")

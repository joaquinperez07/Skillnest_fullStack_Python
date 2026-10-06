from flask import request, redirect, session, flash
from flask_app import app
from flask_app.models.task import Task
from flask_app.models.comment import Comment
from flask_app.utils import login_required


@app.route("/tareas/<int:task_id>/comentar", methods=["POST"])
@login_required
def add_comment(task_id):
    uid = session["user_id"]
    if not Task.get_one(task_id, uid):
        flash("La tarea no existe o no tienes permiso para comentarla.", "error")
        return redirect("/dashboard")
    if Comment.validate(request.form):
        Comment.create({"content": request.form["content"].strip(), "task_id": task_id, "user_id": uid})
        flash("Comentario agregado.", "success")
    return redirect(f"/tareas/{task_id}")


@app.route("/comentarios/borrar/<int:comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.get_one(comment_id)
    if not comment or comment["user_id"] != session["user_id"]:
        flash("No tienes permiso para borrar este comentario.", "error")
        return redirect("/dashboard")
    Comment.delete(comment_id, session["user_id"])
    flash("Comentario eliminado.", "success")
    return redirect(f"/tareas/{comment['task_id']}")

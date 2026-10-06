from flask import render_template, request, redirect, session, flash
from flask_app import app
from flask_app.models.category import Category
from flask_app.models.task import Task
from flask_app.utils import login_required


@app.route("/categorias")
@login_required
def categories():
    return render_template("categories.html", categories=Category.get_all_by_user(session["user_id"]))


@app.route("/categorias/nueva")
@login_required
def new_category():
    return render_template("category_form.html", category=None, form=session.pop("form", {}))


@app.route("/categorias/crear", methods=["POST"])
@login_required
def create_category():
    uid = session["user_id"]
    if not Category.validate(request.form, uid):
        session["form"] = request.form.to_dict()
        return redirect("/categorias/nueva")
    Category.create({"name": request.form["name"].strip(), "user_id": uid})
    flash("Categoría creada correctamente.", "success")
    return redirect("/categorias")


@app.route("/categorias/<int:category_id>")
@login_required
def show_category(category_id):
    cat = Category.get_one(category_id, session["user_id"])
    if not cat:
        flash("La categoría no existe o no tienes permiso para verla.", "error")
        return redirect("/categorias")
    return render_template("category_detail.html", category=cat,
                           tasks=Task.get_by_category(session["user_id"], category_id))


@app.route("/categorias/editar/<int:category_id>")
@login_required
def edit_category(category_id):
    cat = Category.get_one(category_id, session["user_id"])
    if not cat:
        flash("La categoría no existe o no tienes permiso para editarla.", "error")
        return redirect("/categorias")
    return render_template("category_form.html", category=cat, form=session.pop("form", {}))


@app.route("/categorias/actualizar/<int:category_id>", methods=["POST"])
@login_required
def update_category(category_id):
    uid = session["user_id"]
    if not Category.get_one(category_id, uid):
        flash("La categoría no existe o no tienes permiso para editarla.", "error")
        return redirect("/categorias")
    if not Category.validate(request.form, uid, exclude_id=category_id):
        session["form"] = request.form.to_dict()
        return redirect(f"/categorias/editar/{category_id}")
    Category.update({"id": category_id, "user_id": uid, "name": request.form["name"].strip()})
    flash("Categoría actualizada correctamente.", "success")
    return redirect("/categorias")


@app.route("/categorias/borrar/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    uid = session["user_id"]
    if not Category.get_one(category_id, uid):
        flash("La categoría no existe o no tienes permiso para borrarla.", "error")
    elif Category.count_tasks(category_id) > 0:
        flash("No puedes borrar una categoría que tiene tareas asociadas.", "error")
    else:
        Category.delete(category_id, uid)
        flash("Categoría eliminada.", "success")
    return redirect("/categorias")

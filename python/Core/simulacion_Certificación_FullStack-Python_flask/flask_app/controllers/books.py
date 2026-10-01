from flask import abort, flash, redirect, render_template, request, session

from flask_app import app
from flask_app.controllers.users import login_required
from flask_app.models.book import GENRES, Book


def _form_data(form):
    return {
        "title": form["title"].strip(),
        "author": form["author"].strip(),
        "genre": form["genre"],
        "publication_date": form["publication_date"],
        "description": form["description"].strip(),
    }


@app.route("/libros")
@login_required
def my_books():
    uid = session["user_id"]
    return render_template(
        "books/index.html",
        my_books=Book.get_by_user(uid),
        community_books=Book.get_community(uid),
    )


@app.route("/explorar")
@login_required
def explore():
    return render_template("books/explore.html", books=Book.get_all())


@app.route("/libros/nuevo")
@login_required
def new_book():
    form_data = session.pop("form_data", None)
    return render_template("books/new.html", genres=GENRES, form_data=form_data)


@app.route("/libros/crear", methods=["POST"])
@login_required
def create_book():
    if not Book.validate(request.form):
        session["form_data"] = request.form.to_dict()
        return redirect("/libros/nuevo")
    data = _form_data(request.form)
    data["user_id"] = session["user_id"]
    Book.create(data)
    session.pop("form_data", None)
    flash("Libro agregado correctamente.", "success")
    return redirect("/libros")


@app.route("/libros/<int:book_id>")
@login_required
def show_book(book_id):
    book = Book.get_one(book_id)
    if not book:
        abort(404)
    return render_template(
        "books/show.html",
        book=book,
        fans=Book.get_favorited_by(book_id),
        is_favorite=Book.is_favorite(session["user_id"], book_id),
    )


@app.route("/libros/editar/<int:book_id>")
@login_required
def edit_book(book_id):
    book = Book.get_one(book_id)
    if not book:
        abort(404)
    if book["user_id"] != session["user_id"]:
        flash("No tienes permiso para editar este libro.", "book")
        return redirect("/libros")
    # Si hubo error de validación se repueblan los datos enviados
    form_data = session.pop("form_data", None)
    return render_template("books/edit.html", book=book, genres=GENRES, form_data=form_data)


@app.route("/libros/actualizar/<int:book_id>", methods=["POST"])
@login_required
def update_book(book_id):
    book = Book.get_one(book_id)
    if not book:
        abort(404)
    if book["user_id"] != session["user_id"]:
        flash("No tienes permiso para editar este libro.", "book")
        return redirect("/libros")
    if not Book.validate(request.form, original_date=book["publication_date"]):
        session["form_data"] = request.form.to_dict()
        return redirect(f"/libros/editar/{book_id}")
    data = _form_data(request.form)
    data.update({"id": book_id, "user_id": session["user_id"]})
    Book.update(data)
    flash("Libro actualizado correctamente.", "success")
    return redirect("/libros")


@app.route("/libros/borrar/<int:book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    book = Book.get_one(book_id)
    if not book:
        abort(404)
    if book["user_id"] != session["user_id"]:
        flash("No tienes permiso para eliminar este libro.", "book")
        return redirect("/libros")
    Book.delete(book_id, session["user_id"])
    flash("Libro eliminado.", "success")
    return redirect("/libros")


@app.route("/favoritos")
@login_required
def favorites():
    return render_template("books/favorites.html", books=Book.get_favorites_of_user(session["user_id"]))


@app.route("/favoritos/agregar/<int:book_id>", methods=["POST"])
@login_required
def add_favorite(book_id):
    if not Book.get_one(book_id):
        abort(404)
    Book.add_favorite(session["user_id"], book_id)
    flash("Libro agregado a tus favoritos.", "success")
    return redirect(f"/libros/{book_id}")

from flask_app import app
from flask import render_template, request, redirect, url_for, flash

from flask_app.models.usuario import Usuario
from flask_app.models.seguidor import Seguidor


@app.route("/")
def inicio():
    return redirect(url_for("usuarios"))


@app.route("/usuarios")
def usuarios():
    return render_template(
        "usuarios.html",
        usuarios=Usuario.get_all(),
        relaciones=Seguidor.get_all()
    )


@app.route("/usuarios/crear", methods=["POST"])
def crear_usuario():
    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    email = request.form.get("email", "").strip()

    if not nombre or not apellido or not email:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("usuarios"))

    resultado = Usuario.save({
        "nombre": nombre,
        "apellido": apellido,
        "email": email
    })

    if resultado is False:
        flash("No fue posible crear el usuario.", "danger")
        return redirect(url_for("usuarios"))

    flash("Usuario creado correctamente.", "success")
    return redirect(url_for("usuarios"))


@app.route("/seguir", methods=["POST"])
def seguir():
    """
    usuario_id: usuario que está siendo seguido.
    seguidor_id: usuario que lo sigue.
    """
    usuario_id_texto = request.form.get("usuario_id")
    seguidor_id_texto = request.form.get("seguidor_id")

    if not usuario_id_texto or not seguidor_id_texto:
        flash("Debes seleccionar un usuario y un seguidor.", "danger")
        return redirect(url_for("usuarios"))

    try:
        usuario_id = int(usuario_id_texto)
        seguidor_id = int(seguidor_id_texto)
    except ValueError:
        flash("Los identificadores no son válidos.", "danger")
        return redirect(url_for("usuarios"))

    if Usuario.get_by_id(usuario_id) is None:
        flash("El usuario seleccionado no existe.", "danger")
        return redirect(url_for("usuarios"))

    if Usuario.get_by_id(seguidor_id) is None:
        flash("El seguidor seleccionado no existe.", "danger")
        return redirect(url_for("usuarios"))

    data = {"usuario_id": usuario_id, "seguidor_id": seguidor_id}

    if Seguidor.existe(data):
        flash("Esta relación ya existe.", "warning")
        return redirect(url_for("usuarios"))

    if Seguidor.seguir(data) is False:
        flash("No fue posible registrar la relación.", "danger")
        return redirect(url_for("usuarios"))

    flash("Relación registrada correctamente.", "success")
    return redirect(url_for("usuarios"))

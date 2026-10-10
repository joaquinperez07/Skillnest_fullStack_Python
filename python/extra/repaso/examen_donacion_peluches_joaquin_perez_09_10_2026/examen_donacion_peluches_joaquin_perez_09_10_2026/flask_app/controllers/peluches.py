from flask import redirect, render_template, request, session

from flask_app import app
from flask_app.models.peluche import Peluche
from flask_app.utils import login_requerido


@app.route("/dashboard")
@login_requerido
def dashboard():
    return render_template("dashboard.html", peluches=Peluche.obtener_todos())


@app.route("/nueva")
@login_requerido
def nueva():
    return render_template("nueva.html")


@app.route("/crear", methods=["POST"])
@login_requerido
def crear():
    if not Peluche.validar(request.form):
        return redirect("/nueva")

    Peluche.crear({
        "nombre": request.form["nombre"].strip(),
        "descripcion": request.form["descripcion"].strip(),
        "donador_id": session["usuario_id"],
    })
    return redirect("/dashboard")


@app.route("/ver/<int:peluche_id>")
@login_requerido
def ver(peluche_id):
    peluche = Peluche.obtener_uno(peluche_id)
    if not peluche:
        return redirect("/dashboard")
    Peluche.sumar_visita(peluche_id)
    peluche.visitas += 1
    return render_template("ver.html", peluche=peluche)


@app.route("/editar/<int:peluche_id>")
@login_requerido
def editar(peluche_id):
    peluche = Peluche.obtener_uno(peluche_id)
    if not peluche or peluche.donador_id != session["usuario_id"]:
        return redirect("/dashboard")
    return render_template("editar.html", peluche=peluche)


@app.route("/actualizar/<int:peluche_id>", methods=["POST"])
@login_requerido
def actualizar(peluche_id):
    peluche = Peluche.obtener_uno(peluche_id)
    if not peluche or peluche.donador_id != session["usuario_id"]:
        return redirect("/dashboard")

    if not Peluche.validar(request.form, excluir_id=peluche_id):
        return redirect(f"/editar/{peluche_id}")

    Peluche.actualizar({
        "id": peluche_id,
        "nombre": request.form["nombre"].strip(),
        "descripcion": request.form["descripcion"].strip(),
        "donador_id": session["usuario_id"],
    })
    return redirect("/dashboard")


@app.route("/borrar/<int:peluche_id>", methods=["POST"])
@login_requerido
def borrar(peluche_id):
    Peluche.eliminar({"id": peluche_id, "donador_id": session["usuario_id"]})
    return redirect("/dashboard")


@app.route("/adoptar/<int:peluche_id>", methods=["POST"])
@login_requerido
def adoptar(peluche_id):
    Peluche.adoptar({"id": peluche_id, "usuario_id": session["usuario_id"]})
    return redirect("/dashboard")

from flask import flash

from flask_app.config.mysql_connection import connect_to_mysql

# Cada peluche junto al nombre de quien lo donó y (si existe) de quien lo adoptó
SELECT_BASE = """
    SELECT p.*,
           d.nombre AS donador,
           a.nombre AS adoptante
    FROM peluches p
    JOIN usuarios d ON d.id = p.donador_id
    LEFT JOIN usuarios a ON a.id = p.adoptante_id
"""


class Peluche:
    def __init__(self, data):
        self.id = data["id"]
        self.nombre = data["nombre"]
        self.descripcion = data["descripcion"]
        self.visitas = data["visitas"]
        self.donador_id = data["donador_id"]
        self.adoptante_id = data["adoptante_id"]
        self.donador = data["donador"]
        self.adoptante = data["adoptante"]

    @classmethod
    def obtener_todos(cls):
        filas = connect_to_mysql().query_db(SELECT_BASE + " ORDER BY p.id;")
        return [cls(f) for f in filas] if filas else []

    @classmethod
    def obtener_uno(cls, peluche_id):
        fila = connect_to_mysql().query_db(
            SELECT_BASE + " WHERE p.id = %(id)s;", {"id": peluche_id}
        )
        return cls(fila[0]) if fila else None

    @classmethod
    def crear(cls, data):
        query = """
            INSERT INTO peluches (nombre, descripcion, donador_id)
            VALUES (%(nombre)s, %(descripcion)s, %(donador_id)s);
        """
        return connect_to_mysql().query_db(query, data)

    @classmethod
    def actualizar(cls, data):
        query = """
            UPDATE peluches SET nombre = %(nombre)s, descripcion = %(descripcion)s
            WHERE id = %(id)s AND donador_id = %(donador_id)s;
        """
        return connect_to_mysql().query_db(query, data)

    @classmethod
    def eliminar(cls, data):
        query = "DELETE FROM peluches WHERE id = %(id)s AND donador_id = %(donador_id)s;"
        return connect_to_mysql().query_db(query, data)

    @classmethod
    def adoptar(cls, data):
        # Solo si nadie lo adoptó y quien adopta no es el donador
        query = """
            UPDATE peluches SET adoptante_id = %(usuario_id)s
            WHERE id = %(id)s AND adoptante_id IS NULL AND donador_id != %(usuario_id)s;
        """
        return connect_to_mysql().query_db(query, data)

    @classmethod
    def sumar_visita(cls, peluche_id):
        query = "UPDATE peluches SET visitas = visitas + 1 WHERE id = %(id)s;"
        return connect_to_mysql().query_db(query, {"id": peluche_id})

    @staticmethod
    def nombre_en_uso(nombre, excluir_id=None):
        query = "SELECT id FROM peluches WHERE nombre = %(nombre)s"
        data = {"nombre": nombre}
        if excluir_id:
            query += " AND id != %(excluir_id)s"
            data["excluir_id"] = excluir_id
        return bool(connect_to_mysql().query_db(query + ";", data))

    @staticmethod
    def validar(form, excluir_id=None):
        valido = True
        nombre = form["nombre"].strip()
        descripcion = form["descripcion"].strip()
        if not nombre:
            flash("El nombre no puede estar vacío.", "peluche")
            valido = False
        elif Peluche.nombre_en_uso(nombre, excluir_id):
            flash("Ya existe un peluche con ese nombre.", "peluche")
            valido = False
        if not descripcion:
            flash("La descripción no puede estar vacía.", "peluche")
            valido = False
        return valido

from flask_app.config.mysqlconnection import connectToMySQL

DB = "esquema_seguidores"


class Usuario:
    """Representa un registro de la tabla usuarios."""

    def __init__(self, data):
        self.id = data["id"]
        self.nombre = data["nombre"]
        self.apellido = data["apellido"]
        self.email = data["email"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]

    @classmethod
    def get_all(cls):
        query = """
            SELECT id, nombre, apellido, email, created_at, updated_at
            FROM usuarios
            ORDER BY nombre, apellido;
        """
        resultados = connectToMySQL(DB).query_db(query)
        return [cls(u) for u in resultados] if resultados else []

    @classmethod
    def get_by_id(cls, id):
        query = """
            SELECT id, nombre, apellido, email, created_at, updated_at
            FROM usuarios
            WHERE id = %(id)s;
        """
        resultado = connectToMySQL(DB).query_db(query, {"id": id})
        if resultado:
            return cls(resultado[0])
        return None

    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO usuarios (nombre, apellido, email)
            VALUES (%(nombre)s, %(apellido)s, %(email)s);
        """
        return connectToMySQL(DB).query_db(query, data)

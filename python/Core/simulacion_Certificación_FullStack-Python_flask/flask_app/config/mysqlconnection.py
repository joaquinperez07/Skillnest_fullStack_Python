import os

import pymysql.cursors


class MySQLConnection:
    """Conexión a MySQL con PyMySQL. Cada consulta abre y cierra su conexión."""

    def __init__(self, db):
        self.connection = pymysql.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "1234"),
            db=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def query_db(self, query, data=None):
        """SELECT -> lista de dicts | INSERT -> id insertado | UPDATE/DELETE -> filas afectadas."""
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, data)
                sql = query.strip().lower()
                if sql.startswith("insert"):
                    self.connection.commit()
                    return cursor.lastrowid
                if sql.startswith("select"):
                    return list(cursor.fetchall())
                self.connection.commit()
                return cursor.rowcount
            except Exception as error:
                self.connection.rollback()
                print("Error en la consulta:", error)
                return False
            finally:
                self.connection.close()


def connectToMySQL(db):
    return MySQLConnection(db)

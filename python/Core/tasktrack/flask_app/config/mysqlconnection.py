import os
import pymysql.cursors


class MySQLConnection:
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
        """SELECT -> lista de dicts | INSERT -> id insertado | UPDATE/DELETE -> filas afectadas.
        Siempre usa consultas parametrizadas (evita SQL injection)."""
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, data)
                verb = query.strip().lower().split()[0]
                if verb == "insert":
                    self.connection.commit()
                    return cursor.lastrowid
                if verb == "select":
                    return cursor.fetchall()
                self.connection.commit()
                return cursor.rowcount
            except Exception as e:
                self.connection.rollback()
                print("Error en la consulta:", e)
                return False
            finally:
                self.connection.close()


def connectToMySQL(db="tasktrack_db"):
    return MySQLConnection(db)

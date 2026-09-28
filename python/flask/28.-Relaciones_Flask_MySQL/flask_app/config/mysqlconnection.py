import pymysql.cursors


class MySQLConnection:
    """Administra una conexión con MySQL."""

    def __init__(self, db):
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

    def query_db(self, query, data=None):
        """
        SELECT: lista de diccionarios.
        INSERT: ID generado.
        UPDATE / DELETE: filas afectadas.
        Error: False.
        """
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, data)

                if query.strip().lower().startswith("select"):
                    return cursor.fetchall()

                if query.strip().lower().startswith("insert"):
                    return cursor.lastrowid

                return cursor.rowcount

            except Exception as e:
                print("Something went wrong:", e)
                return False

            finally:
                self.connection.close()


def connectToMySQL(db):
    return MySQLConnection(db)

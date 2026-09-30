import pymysql.cursors


class MySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="1234", 
            db=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def query_db(self, query, data=None):
        """SELECT -> lista de dicts | INSERT -> id insertado | UPDATE/DELETE -> None"""
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, data)
                if query.lstrip().lower().startswith("insert"):
                    self.connection.commit()
                    return cursor.lastrowid
                if query.lstrip().lower().startswith("select"):
                    return cursor.fetchall()
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                print("Error en la consulta:", e)
                return False
            finally:
                self.connection.close()


def connectToMySQL(db):
    return MySQLConnection(db)

import os

import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()


class MySQLConnection:
    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DATABASE"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def query_db(self, query, data=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, data)
                tipo = query.lstrip().split(None, 1)[0].lower()
                if tipo == "insert":
                    return cursor.lastrowid
                if tipo == "select":
                    return cursor.fetchall()
                return cursor.rowcount
        except Exception as error:
            print("Error en la consulta:", error)
            return False
        finally:
            self.connection.close()


def connect_to_mysql():
    return MySQLConnection()

import os

from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bookhub-clave-secreta-cambiar-en-produccion")

bcrypt = Bcrypt(app)

DATABASE = os.environ.get("DB_NAME", "bookhub_db")

# Punto de entrada
from flask_app import app

# Carga las rutas definidas en flask_app/controllers/tacos.py
from flask_app.controllers import tacos

if __name__ == "__main__":
    app.run(debug=True)

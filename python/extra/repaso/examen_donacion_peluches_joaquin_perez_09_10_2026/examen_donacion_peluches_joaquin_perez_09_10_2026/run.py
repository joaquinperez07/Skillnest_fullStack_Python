from flask_app import app

# Al importar los controladores se registran sus rutas
from flask_app.controllers import usuarios, peluches  # noqa: F401

if __name__ == "__main__":
    app.run(debug=True)

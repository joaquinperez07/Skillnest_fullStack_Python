from flask_app import app
from flask_app.controllers import users, tasks, categories, comments  # noqa: F401  (registra rutas)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

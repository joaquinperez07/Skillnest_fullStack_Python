# BookHub

Aplicación web para compartir, descubrir y marcar como favoritos libros. Construida con **Flask, MySQL, PyMySQL, Jinja2, Bootstrap 5, Flask-Bcrypt** y arquitectura **MVC modularizada**.

## Estructura

```
bookhub/
├── server.py                     # Punto de entrada
├── requirements.txt
├── resources/
│   ├── schema.sql                # Script de la base de datos
│   ├── erd.md                    # ERD (Mermaid)
│   └── erd.svg                   # ERD (imagen)
└── flask_app/
    ├── __init__.py               # app, secret key, Bcrypt
    ├── config/mysqlconnection.py # Conexión PyMySQL
    ├── models/                   # user.py, book.py (consultas + validaciones)
    ├── controllers/              # users.py (auth), books.py (CRUD + favoritos)
    ├── templates/                # Vistas Jinja2 + Bootstrap
    └── static/css/style.css
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
mysql -u root -p < resources/schema.sql
python server.py
```

Abrir http://localhost:5000

Credenciales de MySQL por variables de entorno (valores por defecto entre paréntesis):
`DB_HOST` (localhost), `DB_USER` (root), `DB_PASSWORD` (root), `DB_NAME` (bookhub_db), `SECRET_KEY`.

## Rutas

| Ruta | Método | Descripción |
|---|---|---|
| `/` | GET | Login / Registro |
| `/registro`, `/login`, `/logout` | POST / POST / GET | Autenticación (Bcrypt) |
| `/libros` | GET | Mis libros + libros de la comunidad |
| `/explorar` | GET | Todos los libros |
| `/libros/nuevo` · `/libros/crear` | GET · POST | Crear libro |
| `/libros/<id>` | GET | Detalle y usuarios que lo marcaron favorito |
| `/libros/editar/<id>` · `/libros/actualizar/<id>` | GET · POST | Editar (solo dueño) |
| `/libros/borrar/<id>` | POST | Eliminar (solo dueño) |
| `/favoritos` · `/favoritos/agregar/<id>` | GET · POST | Favoritos |

## Reglas implementadas

- Registro: nombre y apellido ≥ 2 caracteres, e-mail válido y único, contraseña ≥ 8 y confirmación igual. Contraseña almacenada con Bcrypt.
- Libro: todos los campos obligatorios, título ≥ 2, género seleccionado, fecha no pasada, descripción ≥ 10. En edición se permite conservar la fecha ya guardada.
- Rutas protegidas con decorador `login_required` y sesión.
- Solo el dueño puede editar/borrar: se valida en el controlador y también en el SQL (`WHERE id = ... AND user_id = ...`).
- Relaciones: `users 1:N books` y `users N:M books` (tabla `favorites`).
- El botón "Agregar a Favoritos" desaparece si el usuario ya lo agregó.

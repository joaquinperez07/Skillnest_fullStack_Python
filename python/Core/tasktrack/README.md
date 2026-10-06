# TaskTrack — Gestión de Tareas (Flask + MySQL)

Aplicación web con arquitectura **MVC**: registro/login con **Bcrypt**, sesiones, CRUD de tareas y categorías,
comentarios, validaciones y plantillas **Jinja2**.

## Puesta en marcha

```bash
pip install -r requirements.txt
mysql -u root -p < schema.sql        # crea la BD tasktrack_db y las tablas
python server.py                      # http://localhost:5000
```

Credenciales de MySQL (por defecto `root` / `root` en `localhost`), configurables con variables de entorno:
`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`.

## Estructura

```
server.py                      # punto de entrada
schema.sql                     # esquema MySQL
flask_app/
  config/mysqlconnection.py    # conexión (consultas parametrizadas)
  models/   user.py category.py task.py comment.py   # consultas + validaciones
  controllers/ users.py tasks.py categories.py comments.py
  templates/                   # Jinja2 (base + una vista por pantalla del wireframe)
  static/css/style.css
```

## Relaciones entre tablas
- `users` 1—N `categories`, `users` 1—N `tasks`, `categories` 1—N `tasks`, `tasks` 1—N `comments`, `users` 1—N `comments`.

## Rutas (según wireframe)
| Ruta | Descripción |
|---|---|
| `/` | Login / Registro |
| `/dashboard` | Mis Tareas, próximas tareas, resumen, filtro por estado y búsqueda por título |
| `/tareas/nueva` · `/tareas/crear` | Crear tarea |
| `/tareas/<id>` | Detalle + comentarios |
| `/tareas/editar/<id>` · `/tareas/actualizar/<id>` | Editar (formulario pre-poblado) |
| `/tareas/completar/<id>` · `/tareas/borrar/<id>` | Marcar completada / borrar (POST) |
| `/categorias` (+ `nueva`, `crear`, `editar`, `actualizar`, `borrar`, `/<id>`) | CRUD de categorías con total de tareas |
| `/perfil` · `/logout` | Perfil y cierre de sesión |

## Validaciones
- **Registro:** nombre y apellido ≥ 2 caracteres, email válido y único, contraseña ≥ 8 y confirmación igual, mensajes con `flash`.
- **Login:** el email debe existir y la contraseña coincidir con el hash (mismo mensaje en ambos casos).
- **Tarea:** campos obligatorios, título ≥ 3, categoría y prioridad seleccionadas, fecha no pasada, descripción ≥ 10.
- **Categoría:** nombre ≥ 3 y único por usuario.

## Seguridad y permisos
- Contraseñas con Bcrypt; rutas protegidas con `@login_required`.
- Todas las consultas de tareas/categorías filtran por `user_id`: un usuario no puede ver, editar ni borrar datos ajenos (aunque cambie el ID en la URL).
- Borrados y cambios de estado por **POST**; solo el autor puede borrar su comentario.
- Una categoría con tareas no puede borrarse.

## Bonus implementados
Marcar como completada · filtro por estado · búsqueda por título · solo tareas futuras en "Próximas" · cantidad de tareas por prioridad · comentarios solo del usuario autenticado · prevención de acceso a tareas ajenas · datos del formulario se conservan al fallar la validación.

# Validación de email con base de datos

Proyecto Flask + MySQL que implementa validación de formularios, expresiones
regulares, mensajes flash, sesiones y verificación de email único.

## Instalación

```bash
pipenv install flask pymysql
```

## Base de datos

1. Abre MySQL y ejecuta el script:

```bash
mysql -u root -p < flask_app/bd/esquema_usuarios.sql
```

o simplemente pega el contenido de `flask_app/bd/esquema_usuarios.sql`
en tu cliente MySQL (Workbench, DBeaver, etc.).

2. Verifica la conexión en `flask_app/config/mysqlconnection.py` — ajusta
   `user` y `password` según tu configuración local.

## Ejecutar el servidor

```bash
pipenv run python server.py
```

Luego abre: http://localhost:5000

## Pendiente por hacer tú

- **ERD**: el repositorio debe incluir `resources/esquema_usuarios_erd.mwb`.
  Genera este archivo abriendo MySQL Workbench, modelando la tabla
  `usuarios` (ver diagrama abajo) y guardándolo en esa carpeta — no puedo
  generar un archivo `.mwb` binario desde aquí.

```
usuarios
├── id             PK, INT AUTO_INCREMENT
├── nombre         VARCHAR(100)
├── apellido       VARCHAR(100)
├── email          VARCHAR(100) UNIQUE
├── created_at     DATETIME
└── updated_at     DATETIME
```

- **Capturas de pantalla**: toma evidencia de:
  1. El listado de usuarios (`/usuarios`)
  2. El formulario de creación mostrando un mensaje de validación
     (por ejemplo, email inválido)

- **Datos de conexión MySQL**: revisa `flask_app/config/mysqlconnection.py`
  antes de ejecutar, por si tu usuario/contraseña de MySQL son distintos
  de `root` / (vacío).

## Estructura

```
usuarios_validacion/
│
├── flask_app/
│   ├── __init__.py
│   ├── bd/esquema_usuarios.sql
│   ├── config/mysqlconnection.py
│   ├── controllers/usuarios.py
│   ├── models/usuario.py
│   ├── templates/usuarios.html
│   ├── templates/nuevo_usuario.html
│   └── static/css/style.css
│
├── resources/            (agrega aquí el ERD .mwb)
├── Pipfile
├── .gitignore
└── server.py
```

## Rutas

| Método | Ruta               | Función                    |
|--------|--------------------|-----------------------------|
| GET    | /                  | Redirige a /usuarios         |
| GET    | /usuarios          | Muestra listado de usuarios  |
| GET    | /usuarios/nuevo    | Muestra formulario           |
| POST   | /usuarios/crear    | Valida y crea usuario        |

## Validaciones implementadas

- Nombre obligatorio
- Apellido obligatorio
- Email obligatorio y con formato válido (regex)
- Email único (comprobado en Python y forzado con `UNIQUE` en MySQL)
- Los datos del formulario se conservan en `session` cuando hay un error,
  para que el usuario no tenga que reescribirlos todos.

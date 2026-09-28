# Seguidores — Self Join (Flask + MySQL)

1. Ejecuta `flask_app/bd/esquema_seguidores.sql` en MySQL.
2. Ajusta `user` y `password` en `flask_app/config/mysqlconnection.py`.
3. `pipenv install flask pymysql` (genera el Pipfile.lock)
4. `pipenv run python server.py` y abre http://127.0.0.1:5000/usuarios

Nota: falta `resources/esquema_seguidores_erd.mwb` (se exporta desde MySQL Workbench).

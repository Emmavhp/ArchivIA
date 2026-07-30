# SETUP — Cómo preparar este proyecto en otro equipo

Instrucciones rápidas y comprobadas para mover este proyecto a otro computador y dejarlo ejecutando.

1) Requisitos previos
- Instala Python 3.11 (o 3.10+). En Windows: descarga desde python.org y marca "Add Python to PATH".
- (Opcional) Instala Docker si quieres usar contenedor.

2) Clonar el repositorio

Clona el repo que subirás a GitHub:

```bash
git clone git@github.com:TU_USUARIO/TU_REPO.git
cd TU_REPO
```

3) Crear y activar entorno virtual (Windows)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
# o en cmd: .venv\Scripts\activate.bat
```

4) Instalar dependencias

Si ya existe `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Si no estás seguro de que `requirements.txt` esté actualizado, en el equipo original ejecuta:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt || true
pip freeze > requirements.txt
```

5) Variables de entorno y secrets
- No incluyas `.env` en Git. Crea un fichero `.env` local o exporta variables en el sistema.
- Ejemplo mínimo `.env`:

```
# EJEMPLO
FLASK_ENV=development
SECRET_KEY=tu_secreto
```

6) Archivos grandes y outputs
- No subas `outputs/`, `uploads/` ni entornos virtuales al repo. Usa Dropbox/OneDrive o un disco externo para esos ficheros.
- Si usas Dropbox, copia solo las carpetas necesarias (`uploads/`, `outputs/`) en la nueva máquina y respeta la estructura del proyecto.

7) Probar la aplicación

Ejecuta la app según corresponda (ejemplo usando `app.py`):

```powershell
.venv\Scripts\activate
python app.py
# o el comando que uses para arrancar (flask run, uvicorn, etc.)
```

8) (Opcional) Docker — reproducibilidad

Ejemplo de `Dockerfile` mínimo:

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Construir y ejecutar:

```bash
docker build -t archivIA:latest .
docker run -p 5000:5000 --env-file .env archivIA:latest
```

9) Cómo actualizar `requirements.txt` desde el equipo lento (recomendado antes de subir)

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
# Instala paquetes nuevos si es necesario
pip freeze > requirements.txt
```

10) Resumen de qué subir a Git
- Código fuente (`*.py`, `modules/`, `templates/`, `static/`).
- `requirements.txt`, `Dockerfile` (si aplicas), `SETUP.md`, `README.md`.
- No subir: `.venv/`, `outputs/`, `uploads/`, bases de datos locales, `.env`.

Si quieres, creo también un `.gitignore` y un `Dockerfile` base en el repo.

=== Migración paso a paso ===

A continuación un flujo paso a paso para mover el proyecto desde tu portátil lento a otro equipo.

En el equipo original (preparar antes de transferir)

1. Actualiza `requirements.txt` desde el entorno actual:

```powershell
cd C:\ruta\a\tu\repo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt || true
pip freeze > requirements.txt
```

2. Añade/actualiza `.gitignore` (ya está incluido en este repo) y confirma que no subes archivos grandes ni secrets.

3. Haz un backup de `uploads/` y `outputs/` usando el script que creamos (opcional zip):

```powershell
.\scripts\backup_to_dropbox.ps1 -Zip
```

4. Exporta la base de datos si aplica:
- SQLite: simplemente copia el archivo `.db` (por ejemplo `data.db`) a tu backup privado.
- PostgreSQL/MySQL: usa `pg_dump` / `mysqldump` para crear un dump.

5. Confirma que tienes `SETUP.md`, `requirements.txt` y `Dockerfile` en el repo.

6. Inicializa Git y sube al remoto (si aún no lo hiciste):

```bash
git init
git add .
git commit -m "Preparar proyecto para migración"
git remote add origin git@github.com:TU_USUARIO/TU_REPO.git
git push -u origin main
```

En el nuevo equipo (restaurar y ejecutar)

1. Clona el repositorio:

```bash
git clone git@github.com:TU_USUARIO/TU_REPO.git
cd TU_REPO
```

2. Restaurar archivos grandes desde Dropbox:
- Si usaste el script y generaste ZIPs en Dropbox, descárgalos y extrae a la raíz del proyecto (restaurando `uploads/` y `outputs/`).

3. Crear y activar entorno virtual (Windows):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

4. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

5. Restaurar base de datos:
- SQLite: copia el archivo `.db` al lugar esperado.
- PostgreSQL/MySQL: usar `psql` / `mysql` para importar el dump.

6. Configurar variables de entorno:
- Crea un `.env` local con las claves necesarias (no comites `.env`).

7. Probar ejecución:

```powershell
.venv\Scripts\activate
python app.py
# o: flask run  (según cómo arranque tu app)
```

8. (Opcional) Ejecutar via Docker en la nueva máquina:

```bash
docker build -t archivIA:latest .
docker run -p 5000:5000 --env-file .env archivIA:latest
```

Checklist final

- [ ] `requirements.txt` actualizado en el repo
- [ ] Backup de `uploads/` y `outputs` en Dropbox (o copia externa)
- [ ] Dump de base de datos (si aplica)
- [ ] Repo subido a GitHub (o remoto accesible)
- [ ] Nuevo equipo: clonado, venv creado, dependencias instaladas
- [ ] Variables de entorno configuradas y la app arranca correctamente

Si quieres, puedo añadir un script `restore_from_dropbox.ps1` para automatizar la restauración desde los ZIPs que generó el backup.

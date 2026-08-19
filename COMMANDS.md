# COMMANDS — lista de comandos útiles para migrar y restaurar el proyecto

Este archivo contiene todos los comandos copy/paste que necesitas para preparar, respaldar, subir y restaurar el proyecto en otro equipo.

1) Preparar `requirements.txt` en el equipo original

```powershell
cd C:\ruta\a\tu\repo
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt || true
pip freeze > requirements.txt
```

2) Backup de `uploads/` y `outputs/` a Dropbox (script incluido)

```powershell
# Crear ZIPs y guardarlos en la carpeta Dropbox del usuario
.\scripts\backup_to_dropbox.ps1 -Zip

# O copiar las carpetas enteras (sin comprimir)
.\scripts\backup_to_dropbox.ps1
```

3) Subir el repo a GitHub (si no está subido)

```bash
git init
git add .
git commit -m "Preparar proyecto para migración"
git remote add origin git@github.com:TU_USUARIO/TU_REPO.git
git push -u origin main
```

4) En el nuevo equipo: clonar y configurar

```bash
git clone git@github.com:TU_USUARIO/TU_REPO.git
cd TU_REPO
```

5) Crear y activar entorno virtual (Windows)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

6) Instalar dependencias

```powershell
pip install -r requirements.txt
```

7) Restaurar backups desde Dropbox (script incluido)

```powershell
# Extraer todos los ZIPs encontrados en Dropbox
.\scripts\restore_from_dropbox.ps1

# Extraer sólo los ZIPs más recientes (por tipo)
.\scripts\restore_from_dropbox.ps1 -Latest

# Usar ruta de Dropbox alternativa
.\scripts\restore_from_dropbox.ps1 -DropboxPath "D:\Users\Usuario\Dropbox"
```

8) Restaurar base de datos

```powershell
# SQLite: copiar el archivo .db al proyecto
Copy-Item C:\ruta\a\backup\data.db .\data.db

# PostgreSQL example (exportado en el original):
psql -U usuario -d basedatos -f dump.sql
```

9) Ejecutar la app

```powershell
.venv\Scripts\Activate.ps1
python app.py
# o flask run / uvicorn según tu proyecto
```

10) Opcional: Docker build & run

```bash
docker build -t archivIA:latest .
docker run -p 5000:5000 --env-file .env archivIA:latest
```

11) Actualizar `requirements.txt` después de instalar paquetes nuevos

```powershell
.venv\Scripts\Activate.ps1
pip install paquete-nuevo
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Actualizar requirements"
git push
```

Si quieres que incluya comandos para sistemas Linux/macOS (bash), dímelo y los añado.

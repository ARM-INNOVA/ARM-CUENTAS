# Configuración para despliegue en producción
# Render detecta este archivo automáticamente

# Comando de build
build_command: pip install -r backend/requirements.txt && cd backend && python -m alembic upgrade head

# Comando de inicio
start_command: cd backend && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Variables de entorno
env:
  - key: PYTHONUNBUFFERED
    value: "1"
  - key: DEBUG
    value: "False"
  - key: UPLOAD_DIR
    value: "/app/uploads"

# Archivos a ignorar
ignore_files:
  - .git
  - .gitignore
  - frontend/node_modules
  - backend/__pycache__
  - "*.pyc"
  - ".env"

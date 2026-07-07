# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorio persistente por defecto para uploads
RUN mkdir -p /var/data/uploads

# Crear usuario para ejecutar la app
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /var/data
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python init_db.py && gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}"]

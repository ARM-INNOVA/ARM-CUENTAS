import os
import mimetypes
from pathlib import Path
from app.config import settings

def allowed_file(filename: str) -> bool:
    """Verificar si el archivo tiene extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    import re
    # Remover caracteres especiales
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Limitar longitud
    filename = filename[:255]
    return filename

def get_file_extension(filename: str) -> str:
    """Obtener extensión de archivo"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def generate_safe_filename(original_name: str, user_id: int) -> str:
    """Generar nombre de archivo seguro"""
    import uuid
    from datetime import datetime
    
    ext = get_file_extension(original_name)
    safe_name = f"{datetime.utcnow().timestamp()}_{uuid.uuid4().hex}_{user_id}.{ext}"
    return safe_name

def ensure_upload_dir():
    """Asegurar que el directorio de carga existe"""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

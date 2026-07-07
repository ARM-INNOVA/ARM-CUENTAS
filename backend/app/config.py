import os
import logging
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings:
    """Configuración de la aplicación"""
    
    # Entorno
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/arm_cuentas"
    )
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    if SECRET_KEY == "your-secret-key-change-in-production" and ENVIRONMENT == "production":
        raise ValueError("⚠️ SECRET_KEY no está configurada para producción")
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas
    
    # CORS
    CORS_ORIGINS_STR: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    )
    ALLOWED_ORIGINS: list = [origin.strip() for origin in CORS_ORIGINS_STR.split(",")]
    
    # Archivos y almacenamiento
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: set = {"pdf", "jpg", "jpeg", "png", "webp"}
    
    # Aplicación
    APP_NAME: str = "ARM CUENTAS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    AUTH_DISABLED: bool = os.getenv("AUTH_DISABLED", "False").lower() == "true"
    
    # OCR
    USE_OCR: bool = os.getenv("USE_OCR", "True").lower() == "true"
    
    # AWS S3 (opcional)
    USE_S3: bool = os.getenv("USE_S3", "False").lower() == "true"
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")
    AWS_S3_REGION: str = os.getenv("AWS_S3_REGION", "eu-west-1")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

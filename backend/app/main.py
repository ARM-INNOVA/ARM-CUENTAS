from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config import settings, logger
from app.database import init_db
from app.routes import auth, movements, obras, files, categories, providers, exports
import os

# Crear directorios necesarios
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
logger.info(f"📁 Directorio de uploads: {settings.UPLOAD_DIR}")

# Inicializar base de datos
try:
    logger.info("🔄 Inicializando base de datos...")
    init_db()
    logger.info("✅ Base de datos inicializada")
except Exception as e:
    logger.error(f"❌ Error inicializando BD: {e}")

# Crear aplicación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para gestión de ingresos, gastos y facturas",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"🌍 CORS habilitado para: {settings.ALLOWED_ORIGINS}")
logger.info(f"🔐 Entorno: {settings.ENVIRONMENT}")
logger.info(
    f"🔑 Base de datos configurada: {'✅' if settings.DATABASE_URL.startswith(('postgresql://', 'postgresql+psycopg2://', 'sqlite:///')) else '❌'}"
)

# Rutas API
app.include_router(auth.router)
app.include_router(movements.router)
app.include_router(obras.router)
app.include_router(files.router)
app.include_router(categories.router)
app.include_router(providers.router)
app.include_router(exports.router)

# Rutas de info
@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OK",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint para Render Blueprint
    Verifica que la aplicación está funcionando
    """
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "✅ connected",
            "storage": "✅ available"
        }
    except Exception as e:
        logger.error(f"❌ Health check fallido: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.APP_VERSION,
                "error": str(e)
            }
        )

@app.get("/api/health")
async def api_health():
    """Health check para el API"""
    return {
        "status": "ok",
        "app": settings.APP_NAME
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Ruta no encontrada"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

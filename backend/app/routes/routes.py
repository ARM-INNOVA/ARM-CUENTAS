"""
Inicialización de rutas del backend
"""
from app.routes import auth, movements, obras, files, categories, providers, exports

def include_routes(app):
    """Incluir todas las rutas en la aplicación"""
    app.include_router(auth.router)
    app.include_router(movements.router)
    app.include_router(obras.router)
    app.include_router(files.router)
    app.include_router(categories.router)
    app.include_router(providers.router)
    app.include_router(exports.router)
    return app

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.utils.jwt import verify_token
from typing import Callable

async def verify_token_middleware(request: Request, call_next: Callable):
    """Middleware para verificar token JWT"""
    
    # Rutas que no requieren autenticación
    public_routes = ["/api/auth/login", "/api/auth/register", "/docs", "/openapi.json", "/"]
    
    if request.url.path in public_routes or request.url.path.startswith("/static"):
        return await call_next(request)
    
    # Obtener token del header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token no proporcionado"}
        )
    
    token = auth_header.split(" ")[1]
    user_id = verify_token(token)
    
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token inválido o expirado"}
        )
    
    # Agregar user_id al scope para acceso posterior
    request.state.user_id = user_id
    
    return await call_next(request)

from fastapi import Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.utils.jwt import verify_token
from typing import Callable

bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_user_role(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


def _get_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.is_active == True).order_by(User.id.asc()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No hay usuarios disponibles para acceso temporal"
        )
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if settings.AUTH_DISABLED:
        return _get_demo_user(db)

    if not credentials:
        return None

    user_id = verify_token(credentials.credentials)
    if user_id is None:
        return None

    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user_optional(credentials, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    return user


def require_roles(*allowed_roles):
    allowed = {role.value if hasattr(role, "value") else str(role) for role in allowed_roles}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if settings.AUTH_DISABLED:
            return current_user

        if _resolve_user_role(current_user) not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )

        return current_user

    return dependency

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

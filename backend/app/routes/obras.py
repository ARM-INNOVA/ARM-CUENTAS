from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.obra import Obra, ObraStatus
from app.schemas.obra import ObraCreate, ObraUpdate, ObraResponse, ObraDetailResponse
from app.services.movement_service import MovementService
from typing import List

router = APIRouter(prefix="/api/obras", tags=["obras"])

@router.post("/", response_model=ObraResponse, status_code=status.HTTP_201_CREATED)
async def create_obra(
    obra: ObraCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Crear nueva obra"""
    new_obra = Obra(**obra.dict())
    db.add(new_obra)
    db.commit()
    db.refresh(new_obra)
    return ObraResponse.from_orm(new_obra)

@router.get("/{obra_id}", response_model=ObraDetailResponse)
async def get_obra(
    obra_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de una obra"""
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    
    # Calcular resumen
    summary = MovementService.calculate_obra_summary(db, obra_id)
    
    obra_response = ObraDetailResponse.from_orm(obra)
    for key, value in summary.items():
        setattr(obra_response, key, value)
    
    return obra_response

@router.get("/", response_model=List[ObraResponse])
async def list_obras(
    estado: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar obras"""
    query = db.query(Obra)
    
    if estado:
        query = query.filter(Obra.estado == estado)
    else:
        # Por defecto, mostrar solo activas y pausadas
        query = query.filter(Obra.estado.in_([ObraStatus.ACTIVA, ObraStatus.PAUSADA]))
    
    return [ObraResponse.from_orm(o) for o in query.all()]

@router.put("/{obra_id}", response_model=ObraResponse)
async def update_obra(
    obra_id: int,
    obra_update: ObraUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Actualizar obra"""
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    
    update_data = obra_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(obra, field, value)
    
    db.commit()
    db.refresh(obra)
    return ObraResponse.from_orm(obra)

@router.delete("/{obra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_obra(
    obra_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Eliminar obra"""
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if not obra:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    
    db.delete(obra)
    db.commit()
    return None

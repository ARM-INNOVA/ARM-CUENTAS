from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.movement import MovementCreate, MovementUpdate, MovementResponse, MovementDetailResponse
from app.services.movement_service import MovementService
from app.config import logger
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/movements", tags=["movements"])

@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    movement: MovementCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
    db: Session = Depends(get_db)
):
    """Crear nuevo movimiento"""
    new_movement = MovementService.create_movement(db, movement, current_user.id)
    return MovementResponse.from_orm(new_movement)

@router.get("/dashboard/summary", response_model=dict)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener resumen del dashboard"""
    summary = MovementService.calculate_dashboard_summary(db, current_user)
    return summary

@router.get("/{movement_id}", response_model=MovementDetailResponse)
async def get_movement(
    movement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalles de un movimiento"""
    movement = MovementService.get_movement(db, movement_id, current_user)
    return MovementDetailResponse.from_orm(movement)

@router.get("/", response_model=List[MovementResponse])
async def list_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    obra_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    tipo: Optional[str] = None,
    target_user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar movimientos con filtros"""
    movements = MovementService.get_accessible_movements(db, current_user, skip, limit, target_user_id)
    
    # Aplicar filtros adicionales
    if obra_id:
        movements = [m for m in movements if m.obra_id == obra_id]
    if categoria_id:
        movements = [m for m in movements if m.categoria_id == categoria_id]
    if tipo:
        movements = [m for m in movements if m.tipo.value == tipo]

    logger.info("MOVEMENTS_LIST_RETURNED count=%s user_id=%s", len(movements), current_user.id)
    
    return [MovementResponse.from_orm(m) for m in movements]

@router.put("/{movement_id}", response_model=MovementResponse)
async def update_movement(
    movement_id: int,
    movement_update: MovementUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
    db: Session = Depends(get_db)
):
    """Actualizar movimiento"""
    updated_movement = MovementService.update_movement(db, movement_id, current_user, movement_update)
    return MovementResponse.from_orm(updated_movement)

@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movement(
    movement_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
    db: Session = Depends(get_db)
):
    """Eliminar movimiento"""
    MovementService.delete_movement(db, movement_id, current_user)
    return None

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.movement import MovementCreate, MovementUpdate, MovementResponse, MovementDetailResponse
from app.services.movement_service import MovementService
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/movements", tags=["movements"])

# TODO: Agregar dependencia de autenticación

@router.post("/", response_model=MovementResponse, status_code=status.HTTP_201_CREATED)
async def create_movement(
    movement: MovementCreate,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Crear nuevo movimiento"""
    new_movement = MovementService.create_movement(db, movement, user_id)
    return MovementResponse.from_orm(new_movement)

@router.get("/{movement_id}", response_model=MovementDetailResponse)
async def get_movement(
    movement_id: int,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Obtener detalles de un movimiento"""
    movement = MovementService.get_movement(db, movement_id, user_id)
    return MovementDetailResponse.from_orm(movement)

@router.get("/", response_model=List[MovementResponse])
async def list_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    obra_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    tipo: Optional[str] = None,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Listar movimientos con filtros"""
    movements = MovementService.get_user_movements(db, user_id, skip, limit)
    
    # Aplicar filtros adicionales
    if obra_id:
        movements = [m for m in movements if m.obra_id == obra_id]
    if categoria_id:
        movements = [m for m in movements if m.categoria_id == categoria_id]
    if tipo:
        movements = [m for m in movements if m.tipo.value == tipo]
    
    return [MovementResponse.from_orm(m) for m in movements]

@router.put("/{movement_id}", response_model=MovementResponse)
async def update_movement(
    movement_id: int,
    movement_update: MovementUpdate,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Actualizar movimiento"""
    updated_movement = MovementService.update_movement(db, movement_id, user_id, movement_update)
    return MovementResponse.from_orm(updated_movement)

@router.delete("/{movement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movement(
    movement_id: int,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Eliminar movimiento"""
    MovementService.delete_movement(db, movement_id, user_id)
    return None

@router.get("/dashboard/summary", response_model=dict)
async def get_dashboard_summary(
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Obtener resumen del dashboard"""
    summary = MovementService.calculate_dashboard_summary(db, user_id)
    return summary

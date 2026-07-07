from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.movement import Movement
from app.models.obra import Obra
from app.models.user import User
from app.schemas.movement import MovementCreate, MovementUpdate, MovementResponse
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any

class MovementService:
    """Servicio de movimientos"""

    @staticmethod
    def _is_admin(user: User) -> bool:
        role = user.role.value if hasattr(user.role, "value") else str(user.role)
        return role == "admin"
    
    @staticmethod
    def create_movement(db: Session, movement_create: MovementCreate, user_id: int) -> Movement:
        """Crear movimiento"""
        payload = movement_create.model_dump() if hasattr(movement_create, "model_dump") else movement_create.dict()
        payload.pop("needs_review", None)
        movement = Movement(
            **payload,
            user_id=user_id
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement
    
    @staticmethod
    def get_movement(db: Session, movement_id: int, current_user: User) -> Movement:
        """Obtener movimiento"""
        query = db.query(Movement).options(
            joinedload(Movement.obra),
            joinedload(Movement.categoria),
            joinedload(Movement.proveedor),
            joinedload(Movement.user),
            joinedload(Movement.files),
        ).filter(Movement.id == movement_id)

        if not MovementService._is_admin(current_user):
            query = query.filter(Movement.user_id == current_user.id)

        movement = query.first()
        
        if not movement:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        
        return movement
    
    @staticmethod
    def update_movement(db: Session, movement_id: int, current_user: User, update_data: MovementUpdate) -> Movement:
        """Actualizar movimiento"""
        movement = MovementService.get_movement(db, movement_id, current_user)
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(movement, field, value)
        
        movement.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(movement)
        return movement
    
    @staticmethod
    def delete_movement(db: Session, movement_id: int, current_user: User) -> bool:
        """Eliminar movimiento"""
        movement = MovementService.get_movement(db, movement_id, current_user)
        db.delete(movement)
        db.commit()
        return True
    
    @staticmethod
    def get_accessible_movements(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
        target_user_id: Optional[int] = None,
    ) -> List[Movement]:
        """Obtener movimientos visibles para el usuario"""
        query = db.query(Movement).options(
            joinedload(Movement.obra),
            joinedload(Movement.categoria),
            joinedload(Movement.proveedor),
            joinedload(Movement.files),
        )

        if MovementService._is_admin(current_user):
            if target_user_id is not None:
                query = query.filter(Movement.user_id == target_user_id)
        else:
            query = query.filter(Movement.user_id == current_user.id)

        return query.order_by(Movement.fecha.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_movements_by_obra(db: Session, obra_id: int, user_id: int) -> List[Movement]:
        """Obtener movimientos por obra"""
        return db.query(Movement).filter(
            Movement.obra_id == obra_id,
            Movement.user_id == user_id
        ).all()
    
    @staticmethod
    def get_movements_by_date_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Movement]:
        """Obtener movimientos por rango de fechas"""
        return db.query(Movement).filter(
            Movement.user_id == user_id,
            Movement.fecha >= start_date,
            Movement.fecha <= end_date
        ).all()
    
    @staticmethod
    def calculate_obra_summary(db: Session, obra_id: int) -> Dict[str, Any]:
        """Calcular resumen de obra"""
        movements = db.query(Movement).filter(Movement.obra_id == obra_id).all()
        
        ingresos = sum(m.importe_total for m in movements if m.tipo.value == "ingreso")
        gastos = sum(m.importe_total for m in movements if m.tipo.value == "gasto")
        beneficio = ingresos - gastos
        margen = (beneficio / ingresos * 100) if ingresos > 0 else 0
        
        iva_soportado = sum(m.iva_cantidad for m in movements if m.tipo.value == "gasto" and m.iva_cantidad)
        iva_repercutido = sum(m.iva_cantidad for m in movements if m.tipo.value == "ingreso" and m.iva_cantidad)
        
        return {
            "ingresos": float(ingresos),
            "gastos": float(gastos),
            "beneficio": float(beneficio),
            "margen": float(margen),
            "iva_soportado": float(iva_soportado),
            "iva_repercutido": float(iva_repercutido)
        }
    
    @staticmethod
    def calculate_dashboard_summary(db: Session, current_user: User) -> Dict[str, Any]:
        """Calcular resumen del dashboard"""
        now = datetime.utcnow()
        
        # Este mes
        first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_month = (first_day_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        month_query = db.query(Movement).filter(
            Movement.fecha >= first_day_month,
            Movement.fecha <= last_day_month
        )

        if not MovementService._is_admin(current_user):
            month_query = month_query.filter(Movement.user_id == current_user.id)

        movements_month = month_query.all()
        
        # Este año
        first_day_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_year = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        year_query = db.query(Movement).filter(
            Movement.fecha >= first_day_year,
            Movement.fecha <= last_day_year
        )

        if not MovementService._is_admin(current_user):
            year_query = year_query.filter(Movement.user_id == current_user.id)

        movements_year = year_query.all()
        
        def calc_from_movements(movements):
            ingresos = sum(m.importe_total for m in movements if m.tipo.value == "ingreso")
            gastos = sum(m.importe_total for m in movements if m.tipo.value == "gasto")
            beneficio = ingresos - gastos
            iva_soportado = sum(m.iva_cantidad for m in movements if m.tipo.value == "gasto" and m.iva_cantidad)
            iva_repercutido = sum(m.iva_cantidad for m in movements if m.tipo.value == "ingreso" and m.iva_cantidad)
            
            return {
                "ingresos": float(ingresos),
                "gastos": float(gastos),
                "beneficio": float(beneficio),
                "iva_soportado": float(iva_soportado),
                "iva_repercutido": float(iva_repercutido),
                "diferencia_iva": float(iva_repercutido - iva_soportado)
            }
        
        return {
            "mes": calc_from_movements(movements_month),
            "ano": calc_from_movements(movements_year),
            "movimientos_pendientes": len([m for m in movements_month if m.estado.value == "pendiente"]),
            "facturas_pendiente_revision": 0  # TODO: contar facturas sin revisar
        }

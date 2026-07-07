from sqlalchemy.orm import Session
from app.models.obra import Obra
from app.schemas.obra import ObraCreate, ObraUpdate
from typing import List

class ObraService:
    """Servicio de obras"""
    
    @staticmethod
    def create_obra(db: Session, obra_create: ObraCreate) -> Obra:
        """Crear obra"""
        obra = Obra(**obra_create.dict())
        db.add(obra)
        db.commit()
        db.refresh(obra)
        return obra
    
    @staticmethod
    def get_obra(db: Session, obra_id: int) -> Obra:
        """Obtener obra"""
        return db.query(Obra).filter(Obra.id == obra_id).first()
    
    @staticmethod
    def get_obras(db: Session, estado: str = None) -> List[Obra]:
        """Listar obras"""
        query = db.query(Obra)
        
        if estado:
            query = query.filter(Obra.estado == estado)
        else:
            # Por defecto, mostrar activas y pausadas
            from app.models.obra import ObraStatus
            query = query.filter(Obra.estado.in_([ObraStatus.ACTIVA, ObraStatus.PAUSADA]))
        
        return query.all()
    
    @staticmethod
    def search_obra(db: Session, nombre: str) -> List[Obra]:
        """Buscar obra por nombre"""
        return db.query(Obra).filter(
            Obra.nombre.ilike(f"%{nombre}%")
        ).all()
    
    @staticmethod
    def update_obra(db: Session, obra_id: int, update_data: ObraUpdate) -> Obra:
        """Actualizar obra"""
        obra = ObraService.get_obra(db, obra_id)
        if not obra:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(obra, field, value)
        
        db.commit()
        db.refresh(obra)
        return obra
    
    @staticmethod
    def delete_obra(db: Session, obra_id: int) -> bool:
        """Eliminar obra"""
        obra = ObraService.get_obra(db, obra_id)
        if not obra:
            return False
        
        db.delete(obra)
        db.commit()
        return True

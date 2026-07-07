from sqlalchemy.orm import Session
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate
from typing import List

class ProviderService:
    """Servicio de proveedores/clientes"""
    
    @staticmethod
    def create_provider(db: Session, provider_create: ProviderCreate) -> Provider:
        """Crear proveedor"""
        provider = Provider(**provider_create.dict())
        db.add(provider)
        db.commit()
        db.refresh(provider)
        return provider
    
    @staticmethod
    def get_provider(db: Session, provider_id: int) -> Provider:
        """Obtener proveedor"""
        return db.query(Provider).filter(Provider.id == provider_id).first()
    
    @staticmethod
    def get_providers(db: Session, tipo: str = None, activos_only: bool = True) -> List[Provider]:
        """Listar proveedores"""
        query = db.query(Provider)
        
        if activos_only:
            query = query.filter(Provider.activo == True)
        
        if tipo:
            query = query.filter(Provider.tipo == tipo)
        
        return query.all()
    
    @staticmethod
    def search_provider(db: Session, nombre: str) -> List[Provider]:
        """Buscar proveedor por nombre"""
        return db.query(Provider).filter(
            Provider.nombre.ilike(f"%{nombre}%")
        ).all()
    
    @staticmethod
    def update_provider(db: Session, provider_id: int, update_data: ProviderUpdate) -> Provider:
        """Actualizar proveedor"""
        provider = ProviderService.get_provider(db, provider_id)
        if not provider:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(provider, field, value)
        
        db.commit()
        db.refresh(provider)
        return provider
    
    @staticmethod
    def delete_provider(db: Session, provider_id: int) -> bool:
        """Eliminar proveedor"""
        provider = ProviderService.get_provider(db, provider_id)
        if not provider:
            return False
        
        db.delete(provider)
        db.commit()
        return True

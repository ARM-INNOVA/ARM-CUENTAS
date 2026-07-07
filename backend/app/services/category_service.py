from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import List

class CategoryService:
    """Servicio de categorías"""
    
    @staticmethod
    def create_category(db: Session, category_create: CategoryCreate) -> Category:
        """Crear categoría"""
        category = Category(**category_create.dict())
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def get_category(db: Session, category_id: int) -> Category:
        """Obtener categoría"""
        return db.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    def get_categories(db: Session, activas_only: bool = True) -> List[Category]:
        """Listar categorías"""
        query = db.query(Category)
        if activas_only:
            query = query.filter(Category.activa == True)
        return query.all()
    
    @staticmethod
    def update_category(db: Session, category_id: int, update_data: CategoryUpdate) -> Category:
        """Actualizar categoría"""
        category = CategoryService.get_category(db, category_id)
        if not category:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(category, field, value)
        
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Eliminar categoría"""
        category = CategoryService.get_category(db, category_id)
        if not category:
            return False
        
        db.delete(category)
        db.commit()
        return True
    
    @staticmethod
    def get_default_categories():
        """Obtener categorías por defecto"""
        return [
            {"nombre": "Materiales", "descripcion": "Compra de materiales"},
            {"nombre": "Subcontratas", "descripcion": "Trabajos subcontratados"},
            {"nombre": "Herramientas", "descripcion": "Herramientas y equipos"},
            {"nombre": "Maquinaria", "descripcion": "Alquiler de maquinaria"},
            {"nombre": "Combustible", "descripcion": "Gastos de combustible"},
            {"nombre": "Vehículos", "descripcion": "Gastos de vehículos"},
            {"nombre": "Alquileres", "descripcion": "Alquileres de locales o equipos"},
            {"nombre": "Tasas", "descripcion": "Tasas administrativas"},
            {"nombre": "Seguros", "descripcion": "Pólizas de seguros"},
            {"nombre": "Nóminas", "descripcion": "Gastos de personal"},
            {"nombre": "Publicidad", "descripcion": "Gastos publicitarios"},
            {"nombre": "Otros", "descripcion": "Otros gastos"},
            {"nombre": "Ingresos por Servicios", "descripcion": "Ingresos por servicios"},
            {"nombre": "Ingresos por Venta", "descripcion": "Ingresos por venta de productos"},
        ]

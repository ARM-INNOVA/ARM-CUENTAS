"""
Script para inicializar la base de datos con datos por defecto
Uso: python init_db.py
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import Base
from app.models.category import Category
from app.services.category_service import CategoryService

def init_database():
    """Inicializar base de datos con datos por defecto"""
    
    # Crear conexión
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Contar categorías existentes
        existing_categories = db.query(Category).count()
        
        if existing_categories > 0:
            print(f"ℹ️ Base de datos ya inicializada ({existing_categories} categorías)")
            return
        
        # Crear categorías por defecto
        print("📝 Creando categorías por defecto...")
        
        default_categories = CategoryService.get_default_categories()
        
        for cat_data in default_categories:
            category = Category(
                nombre=cat_data["nombre"],
                descripcion=cat_data["descripcion"],
                color="#3B82F6"  # Color azul por defecto
            )
            db.add(category)
        
        db.commit()
        
        print(f"✅ Base de datos inicializada exitosamente")
        print(f"   {len(default_categories)} categorías creadas")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

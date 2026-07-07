"""
Script para inicializar la base de datos con datos por defecto
Uso: python init_db.py
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import Base
from app.models.category import Category
from app.services.category_service import CategoryService


def migrate_provider_activo_to_boolean(engine):
    """Migración defensiva para Render: providers.activo integer -> boolean."""
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as conn:
        exists = conn.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'providers' AND column_name = 'activo'
                """
            )
        ).scalar()

        if not exists:
            return

        current_type = conn.execute(
            text(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'providers' AND column_name = 'activo'
                """
            )
        ).scalar()

        if current_type in {"integer", "smallint", "bigint"}:
            print("🔄 Migrando providers.activo a BOOLEAN...")
            conn.execute(
                text(
                    """
                    ALTER TABLE providers
                    ALTER COLUMN activo TYPE boolean
                    USING activo::integer::boolean
                    """
                )
            )

        # Asegurar restricciones finales aunque ya sea boolean.
        conn.execute(text("UPDATE providers SET activo = true WHERE activo IS NULL"))
        conn.execute(text("ALTER TABLE providers ALTER COLUMN activo SET DEFAULT true"))
        conn.execute(text("ALTER TABLE providers ALTER COLUMN activo SET NOT NULL"))

def init_database():
    """Inicializar base de datos con datos por defecto"""
    
    # Crear conexión
    engine = create_engine(settings.DATABASE_URL)

    # Migraciones defensivas previas a create_all
    migrate_provider_activo_to_boolean(engine)

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

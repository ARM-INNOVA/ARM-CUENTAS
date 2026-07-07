"""
Script para crear usuario administrador inicial
Uso: python create_admin.py
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import Base
from app.models.user import User

DEFAULT_ADMIN_EMAIL = "admin@armcuentas.app"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin123!"

def create_admin():
    """Crear usuario administrador inicial"""
    
    # Crear conexión
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe
        existing_admin = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        if existing_admin:
            updated = False

            if existing_admin.email.endswith(".local"):
                existing_admin.email = DEFAULT_ADMIN_EMAIL
                updated = True

            if existing_admin.role != "admin":
                existing_admin.role = "admin"
                updated = True

            if not existing_admin.is_active:
                existing_admin.is_active = True
                updated = True

            if updated:
                db.commit()
                print("✅ Usuario administrador existente reparado")
            else:
                print("ℹ️ El usuario administrador ya existe")
            return
        
        # Crear admin
        admin = User(
            email=DEFAULT_ADMIN_EMAIL,
            username=DEFAULT_ADMIN_USERNAME,
            full_name="Administrador",
            hashed_password=User.hash_password(DEFAULT_ADMIN_PASSWORD),
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Usuario administrador creado exitosamente")
        print(f"   Username: {DEFAULT_ADMIN_USERNAME}")
        print(f"   Password: {DEFAULT_ADMIN_PASSWORD}")
        print(f"   Email: {DEFAULT_ADMIN_EMAIL}")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error creando administrador: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

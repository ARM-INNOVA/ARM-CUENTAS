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

def create_admin():
    """Crear usuario administrador inicial"""
    
    # Crear conexión
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar si ya existe
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("❌ El usuario administrador ya existe")
            return
        
        # Crear admin
        admin = User(
            email="admin@armcuentas.local",
            username="admin",
            full_name="Administrador",
            hashed_password=User.hash_password("Admin123!"),
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Usuario administrador creado exitosamente")
        print(f"   Username: admin")
        print(f"   Password: Admin123!")
        print(f"   Email: admin@armcuentas.local")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error creando administrador: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

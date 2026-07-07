from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
    nif_cif = Column(String, unique=True)
    email = Column(String)
    telefono = Column(String)
    direccion = Column(String)
    tipo = Column(String)  # "proveedor" o "cliente"
    activo = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movements = relationship("Movement", back_populates="proveedor")
    
    def __repr__(self):
        return f"<Provider {self.nombre}>"

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base

class ObraStatus(str, Enum):
    ACTIVA = "activa"
    PAUSADA = "pausada"
    TERMINADA = "terminada"
    ARCHIVADA = "archivada"

class Obra(Base):
    __tablename__ = "obras"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    cliente = Column(String, nullable=False)
    direccion = Column(String)
    estado = Column(SQLEnum(ObraStatus), default=ObraStatus.ACTIVA)
    fecha_inicio = Column(DateTime)
    fecha_fin_prevista = Column(DateTime)
    presupuesto_previsto = Column(Numeric(12, 2), default=0)
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movements = relationship("Movement", back_populates="obra")
    
    def __repr__(self):
        return f"<Obra {self.nombre}>"

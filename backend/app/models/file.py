from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    movement_id = Column(Integer, ForeignKey("movements.id"), nullable=True)
    
    # Información del archivo
    nombre_original = Column(String, nullable=False)
    nombre_guardado = Column(String, nullable=False, unique=True)
    tipo = Column(String)  # mime type: application/pdf, image/jpeg, etc.
    tamaño = Column(Integer)  # en bytes
    ruta = Column(String, nullable=False)  # ruta local o S3
    
    # Metadatos de extracción
    extraido_automaticamente = Column(Boolean, default=True)
    datos_extraidos = Column(Text)  # JSON con datos extraídos
    confianza_extraccion = Column(Integer, default=0)  # 0-100
    necesita_revision = Column(Boolean, default=False)
    
    # Control
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    movement = relationship("Movement", back_populates="files")
    
    def __repr__(self):
        return f"<File {self.nombre_original}>"

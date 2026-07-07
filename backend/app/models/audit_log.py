from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la acción
    entidad = Column(String)  # "movimento", "obra", "usuario", etc.
    entidad_id = Column(Integer)
    accion = Column(String)  # "crear", "editar", "eliminar"
    cambios = Column(Text)  # JSON con los cambios
    ip_address = Column(String)
    user_agent = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.accion} - {self.entidad}>"

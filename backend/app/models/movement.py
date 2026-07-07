from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.database import Base

class MovementType(str, Enum):
    INGRESO = "ingreso"
    GASTO = "gasto"

class MovementStatus(str, Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    COBRADO = "cobrado"

class PaymentMethod(str, Enum):
    EFECTIVO = "efectivo"
    BANCO = "banco"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    BIZUM = "bizum"
    OTRO = "otro"

class Movement(Base):
    __tablename__ = "movements"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos básicos
    fecha = Column(DateTime, nullable=False)
    tipo = Column(SQLEnum(MovementType), nullable=False)
    concepto = Column(String, nullable=False)
    descripcion = Column(Text)
    
    # Referencias
    obra_id = Column(Integer, ForeignKey("obras.id"))
    categoria_id = Column(Integer, ForeignKey("categories.id"))
    proveedor_id = Column(Integer, ForeignKey("providers.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Datos financieros
    numero_factura = Column(String)
    nif_cif = Column(String)
    base_imponible = Column(Numeric(12, 2), default=0)
    iva_porcentaje = Column(Integer, default=21)  # 21%, 10%, 4%
    iva_cantidad = Column(Numeric(12, 2), default=0)
    importe_total = Column(Numeric(12, 2), nullable=False)
    
    # Estado
    forma_pago = Column(SQLEnum(PaymentMethod), default=PaymentMethod.TRANSFERENCIA)
    estado = Column(SQLEnum(MovementStatus), default=MovementStatus.PENDIENTE)
    observaciones = Column(Text)
    
    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    obra = relationship("Obra", back_populates="movements")
    categoria = relationship("Category", back_populates="movements")
    proveedor = relationship("Provider", back_populates="movements")
    user = relationship("User", back_populates="movements")
    files = relationship("File", back_populates="movement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movement {self.id} - {self.concepto}>"

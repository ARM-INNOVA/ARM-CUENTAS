from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from enum import Enum

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

class MovementBase(BaseModel):
    fecha: datetime
    tipo: MovementType
    concepto: str
    descripcion: Optional[str] = None
    obra_id: Optional[int] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    numero_factura: Optional[str] = None
    nif_cif: Optional[str] = None
    base_imponible: Decimal = Decimal("0")
    iva_porcentaje: int = 21
    iva_cantidad: Decimal = Decimal("0")
    importe_total: Decimal
    forma_pago: PaymentMethod = PaymentMethod.TRANSFERENCIA
    estado: MovementStatus = MovementStatus.PENDIENTE
    observaciones: Optional[str] = None

class MovementCreate(MovementBase):
    pass

class MovementUpdate(BaseModel):
    fecha: Optional[datetime] = None
    tipo: Optional[MovementType] = None
    concepto: Optional[str] = None
    descripcion: Optional[str] = None
    obra_id: Optional[int] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    numero_factura: Optional[str] = None
    nif_cif: Optional[str] = None
    base_imponible: Optional[Decimal] = None
    iva_porcentaje: Optional[int] = None
    iva_cantidad: Optional[Decimal] = None
    importe_total: Optional[Decimal] = None
    forma_pago: Optional[PaymentMethod] = None
    estado: Optional[MovementStatus] = None
    observaciones: Optional[str] = None

class MovementResponse(MovementBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MovementDetailResponse(MovementResponse):
    obra: Optional[dict] = None
    categoria: Optional[dict] = None
    proveedor: Optional[dict] = None
    user: Optional[dict] = None
    files: List[dict] = []

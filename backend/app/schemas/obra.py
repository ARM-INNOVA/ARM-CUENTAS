from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class ObraStatus(str, Enum):
    ACTIVA = "activa"
    PAUSADA = "pausada"
    TERMINADA = "terminada"
    ARCHIVADA = "archivada"

class ObraBase(BaseModel):
    nombre: str
    cliente: str
    direccion: Optional[str] = None
    estado: ObraStatus = ObraStatus.ACTIVA
    fecha_inicio: Optional[datetime] = None
    fecha_fin_prevista: Optional[datetime] = None
    presupuesto_previsto: Optional[Decimal] = None
    observaciones: Optional[str] = None

class ObraCreate(ObraBase):
    pass

class ObraUpdate(BaseModel):
    nombre: Optional[str] = None
    cliente: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[ObraStatus] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin_prevista: Optional[datetime] = None
    presupuesto_previsto: Optional[Decimal] = None
    observaciones: Optional[str] = None

class ObraResponse(ObraBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ObraDetailResponse(ObraResponse):
    ingresos: Decimal = Decimal("0")
    gastos: Decimal = Decimal("0")
    beneficio: Decimal = Decimal("0")
    margen: float = 0.0
    iva_soportado: Decimal = Decimal("0")
    iva_repercutido: Decimal = Decimal("0")

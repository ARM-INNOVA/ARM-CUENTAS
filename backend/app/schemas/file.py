from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.schemas.movement import MovementCreate

class FileBase(BaseModel):
    nombre_original: str
    tipo: Optional[str] = None

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    movement_id: Optional[int] = None
    nombre_guardado: str
    tamaño: Optional[int] = None
    extraido_automaticamente: bool
    confianza_extraccion: int
    necesita_revision: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ExtractedDataResponse(BaseModel):
    """Datos extraídos de una factura"""
    fecha: Optional[str] = None
    numero_factura: Optional[str] = None
    proveedor: Optional[str] = None
    nif_cif: Optional[str] = None
    base_imponible: Optional[float] = None
    iva_porcentaje: Optional[int] = None
    iva_cantidad: Optional[float] = None
    importe_total: Optional[float] = None
    concepto: Optional[str] = None
    texto_extraido: Optional[str] = None
    tipo_detectado: Optional[str] = None
    confianza: int = 0  # 0-100


class FileAttachRequest(BaseModel):
    movement_id: int


class InvoiceReviewRequest(MovementCreate):
    pass

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

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
    invoice_date: Optional[str] = None
    operation_date: Optional[str] = None
    operation_dates: List[str] = Field(default_factory=list)
    sale_date: Optional[str] = None
    invoice_number: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_tax_id: Optional[str] = None
    tax_base: Optional[float] = None
    vat_rate: Optional[int] = None
    vat_amount: Optional[float] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    extracted_text: Optional[str] = None
    confidence: float = 0
    needs_review: bool = True
    warnings: List[str] = Field(default_factory=list)
    field_sources: dict = Field(default_factory=dict)

    # Compatibilidad con formato legado
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
    needs_review: bool = False

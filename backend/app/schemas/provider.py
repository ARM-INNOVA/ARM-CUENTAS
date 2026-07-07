from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class ProviderType(str, Enum):
    PROVEEDOR = "proveedor"
    CLIENTE = "cliente"

class ProviderBase(BaseModel):
    nombre: str
    nif_cif: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo: str = "proveedor"

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(BaseModel):
    nombre: Optional[str] = None
    nif_cif: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None

class ProviderResponse(ProviderBase):
    id: int
    activo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

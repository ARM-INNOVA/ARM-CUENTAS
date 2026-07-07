from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    color: str = "#3B82F6"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    color: Optional[str] = None
    activa: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    activa: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

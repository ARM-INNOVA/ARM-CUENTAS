from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.provider import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse
from app.services.provider_service import ProviderService
from typing import List, Optional

router = APIRouter(prefix="/api/providers", tags=["providers"])

# TODO: Agregar dependencia de autenticación

@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider: ProviderCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo proveedor/cliente"""
    new_provider = ProviderService.create_provider(db, provider)
    return ProviderResponse.from_orm(new_provider)

@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    """Obtener proveedor"""
    provider = ProviderService.get_provider(db, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return ProviderResponse.from_orm(provider)

@router.get("/", response_model=List[ProviderResponse])
async def list_providers(
    tipo: Optional[str] = Query(None),
    activos_only: bool = True,
    db: Session = Depends(get_db)
):
    """Listar proveedores/clientes"""
    providers = ProviderService.get_providers(db, tipo, activos_only)
    return [ProviderResponse.from_orm(p) for p in providers]

@router.get("/search/{nombre}", response_model=List[ProviderResponse])
async def search_providers(
    nombre: str,
    db: Session = Depends(get_db)
):
    """Buscar proveedores por nombre"""
    providers = ProviderService.search_provider(db, nombre)
    return [ProviderResponse.from_orm(p) for p in providers]

@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int,
    provider_update: ProviderUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar proveedor"""
    updated_provider = ProviderService.update_provider(db, provider_id, provider_update)
    if not updated_provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return ProviderResponse.from_orm(updated_provider)

@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar proveedor"""
    if not ProviderService.delete_provider(db, provider_id):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return None

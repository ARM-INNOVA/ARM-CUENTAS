from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService
from typing import List

router = APIRouter(prefix="/api/categories", tags=["categories"])

# TODO: Agregar dependencia de autenticación

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Crear nueva categoría"""
    new_category = CategoryService.create_category(db, category)
    return CategoryResponse.from_orm(new_category)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Obtener categoría"""
    category = CategoryService.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return CategoryResponse.from_orm(category)

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    activas_only: bool = True,
    db: Session = Depends(get_db)
):
    """Listar categorías"""
    categories = CategoryService.get_categories(db, activas_only)
    return [CategoryResponse.from_orm(c) for c in categories]

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar categoría"""
    updated_category = CategoryService.update_category(db, category_id, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return CategoryResponse.from_orm(updated_category)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar categoría"""
    if not CategoryService.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return None

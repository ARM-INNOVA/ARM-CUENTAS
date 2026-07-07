from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.file import File as FileModel
from app.models.movement import Movement
from app.schemas.file import FileResponse, ExtractedDataResponse
from app.utils.files import allowed_file, sanitize_filename, generate_safe_filename, ensure_upload_dir
from app.utils.invoice_extractor import InvoiceExtractor
from app.config import settings
import os
import shutil
import json
from typing import Optional

router = APIRouter(prefix="/api/files", tags=["files"])

# TODO: Agregar dependencia de autenticación

@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    movement_id: Optional[int] = None,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Subir archivo (factura)"""
    
    # Validar extensión
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido"
        )
    
    # Validar tamaño
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Archivo demasiado grande"
        )
    
    # Asegurar directorio de carga
    ensure_upload_dir()
    
    # Generar nombre seguro
    safe_filename = generate_safe_filename(file.filename, user_id)
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Extraer datos si es PDF
    extracted_data = None
    if file.filename.lower().endswith('.pdf'):
        text = InvoiceExtractor.extract_text_from_pdf(file_path)
        extracted_data = InvoiceExtractor.extract_invoice_data(text)
        invoice_type = InvoiceExtractor.detect_invoice_type(text)
    else:
        invoice_type = "gasto"
    
    # Crear registro de archivo
    file_record = FileModel(
        movement_id=movement_id,
        nombre_original=sanitize_filename(file.filename),
        nombre_guardado=safe_filename,
        tipo=file.content_type,
        tamaño=len(contents),
        ruta=file_path,
        datos_extraidos=json.dumps(extracted_data) if extracted_data else None,
        confianza_extraccion=extracted_data.get("confianza", 0) if extracted_data else 0,
        necesita_revision=extracted_data.get("confianza", 0) < 60 if extracted_data else True
    )
    
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    
    return {
        "file_id": file_record.id,
        "nombre_original": file_record.nombre_original,
        "nombre_guardado": file_record.nombre_guardado,
        "tipo_detectado": invoice_type,
        "datos_extraidos": extracted_data,
        "necesita_revision": file_record.necesita_revision
    }

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Obtener información de archivo"""
    file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse.from_orm(file_record)

@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Descargar archivo original"""
    from fastapi.responses import FileResponse as FastAPIFileResponse
    
    file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file_record or not os.path.exists(file_record.ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FastAPIFileResponse(
        path=file_record.ruta,
        filename=file_record.nombre_original
    )

@router.post("/{file_id}/extract", response_model=ExtractedDataResponse)
async def extract_file_data(
    file_id: int,
    user_id: int = 1,  # TODO: Obtener del token
    db: Session = Depends(get_db)
):
    """Extraer datos de archivo"""
    file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file_record or not os.path.exists(file_record.ruta):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    if not file_record.ruta.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se pueden extraer datos de PDFs")
    
    # Extraer datos
    text = InvoiceExtractor.extract_text_from_pdf(file_record.ruta)
    extracted_data = InvoiceExtractor.extract_invoice_data(text)
    
    # Actualizar registro
    file_record.datos_extraidos = json.dumps(extracted_data)
    file_record.confianza_extraccion = extracted_data.get("confianza", 0)
    file_record.necesita_revision = extracted_data.get("confianza", 0) < 60
    db.commit()
    
    return ExtractedDataResponse(**extracted_data)

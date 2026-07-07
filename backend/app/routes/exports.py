from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.export_service import ExportService
from app.services.zip_service import ZipService

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/movements.csv")
async def export_movements_csv(
	year: int | None = Query(None, ge=2000),
	month: int | None = Query(None, ge=1, le=12),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	content = ExportService.export_csv(db, current_user, year, month)
	filename = f"movimientos_{year or 'all'}_{month or 'all'}.csv"
	return Response(
		content=content,
		media_type="text/csv; charset=utf-8",
		headers={"Content-Disposition": f'attachment; filename="{filename}"'},
	)


@router.get("/movements.xlsx")
async def export_movements_excel(
	year: int | None = Query(None, ge=2000),
	month: int | None = Query(None, ge=1, le=12),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	content = ExportService.export_excel(db, current_user, year, month)
	filename = f"movimientos_{year or 'all'}_{month or 'all'}.xlsx"
	return Response(
		content=content,
		media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		headers={"Content-Disposition": f'attachment; filename="{filename}"'},
	)


@router.get("/invoices.zip")
async def export_invoices_zip(
	year: int = Query(..., ge=2000),
	month: int | None = Query(None, ge=1, le=12),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
):
	content = ZipService.build_invoice_zip(db, current_user, year, month)
	filename = f"facturas_{year}_{month or 'all'}.zip"
	return Response(
		content=content,
		media_type="application/zip",
		headers={"Content-Disposition": f'attachment; filename="{filename}"'},
	)
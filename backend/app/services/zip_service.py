from datetime import datetime
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy.orm import Session, joinedload

from app.models.file import File
from app.models.movement import Movement
from app.models.user import User


class ZipService:
	@staticmethod
	def build_invoice_zip(db: Session, current_user: User, year: int, month: int | None = None) -> bytes:
		files = ZipService._query_files(db, current_user, year, month)
		buffer = BytesIO()

		with ZipFile(buffer, "w", ZIP_DEFLATED) as zip_file:
			for file_record in files:
				path = Path(file_record.ruta)
				if not path.exists():
					continue

				zip_name = ZipService._build_name(file_record)
				zip_file.write(path, zip_name)

		return buffer.getvalue()

	@staticmethod
	def _query_files(db: Session, current_user: User, year: int, month: int | None):
		query = db.query(File).options(
			joinedload(File.movement).joinedload(Movement.obra),
			joinedload(File.movement).joinedload(Movement.proveedor),
		)

		role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
		if role != "admin":
			query = query.join(File.movement).filter(Movement.user_id == current_user.id)

		start = datetime(year, month or 1, 1)
		end = datetime(year + (1 if month == 12 else 0), 1 if month == 12 else (month + 1 if month else 1), 1) if month else datetime(year + 1, 1, 1)

		query = query.filter(File.created_at >= start, File.created_at < end)
		return query.all()

	@staticmethod
	def _build_name(file_record: File) -> str:
		movement = file_record.movement
		date_part = (movement.fecha if movement else file_record.created_at).strftime("%Y-%m-%d")
		provider = (movement.proveedor.nombre if movement and movement.proveedor else "Sin-Proveedor").replace(" ", "-")
		amount = f"{float(movement.importe_total):.2f}€" if movement and movement.importe_total is not None else "0.00€"
		obra = (movement.obra.nombre if movement and movement.obra else "Sin-Obra").replace(" ", "-")
		ext = Path(file_record.nombre_original).suffix or Path(file_record.nombre_guardado).suffix or ".pdf"
		return f"{date_part}_{provider}_{amount}_{obra}{ext}"
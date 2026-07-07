import csv
from datetime import datetime
from io import BytesIO, StringIO
from typing import Optional

from openpyxl import Workbook
from sqlalchemy.orm import Session, joinedload

from app.models.movement import Movement
from app.models.user import User


class ExportService:
	HEADERS = [
		"Fecha",
		"Tipo",
		"Concepto",
		"Obra",
		"Categoria",
		"Proveedor/Cliente",
		"Numero factura",
		"NIF/CIF",
		"Base imponible",
		"IVA %",
		"IVA",
		"Importe total",
		"Forma de pago",
		"Estado",
		"Usuario",
	]

	@classmethod
	def export_csv(cls, db: Session, current_user: User, year: Optional[int] = None, month: Optional[int] = None) -> bytes:
		rows = cls._build_rows(db, current_user, year, month)
		buffer = StringIO()
		writer = csv.writer(buffer)
		writer.writerow(cls.HEADERS)
		writer.writerows(rows)
		return buffer.getvalue().encode("utf-8-sig")

	@classmethod
	def export_excel(cls, db: Session, current_user: User, year: Optional[int] = None, month: Optional[int] = None) -> bytes:
		rows = cls._build_rows(db, current_user, year, month)
		workbook = Workbook()
		ws = workbook.active
		ws.title = "Movimientos"
		ws.append(cls.HEADERS)
		for row in rows:
			ws.append(row)
		buffer = BytesIO()
		workbook.save(buffer)
		return buffer.getvalue()

	@classmethod
	def _build_rows(cls, db: Session, current_user: User, year: Optional[int], month: Optional[int]) -> list[list]:
		movements = cls._query_movements(db, current_user, year, month)
		rows = []
		for movement in movements:
			rows.append([
				movement.fecha.strftime("%Y-%m-%d"),
				movement.tipo.value,
				movement.concepto,
				movement.obra.nombre if movement.obra else "",
				movement.categoria.nombre if movement.categoria else "",
				movement.proveedor.nombre if movement.proveedor else "",
				movement.numero_factura or "",
				movement.nif_cif or "",
				float(movement.base_imponible or 0),
				movement.iva_porcentaje or "",
				float(movement.iva_cantidad or 0),
				float(movement.importe_total or 0),
				movement.forma_pago.value if movement.forma_pago else "",
				movement.estado.value if movement.estado else "",
				movement.user.username if movement.user else "",
			])
		return rows

	@staticmethod
	def _query_movements(db: Session, current_user: User, year: Optional[int], month: Optional[int]):
		query = db.query(Movement).options(
			joinedload(Movement.obra),
			joinedload(Movement.categoria),
			joinedload(Movement.proveedor),
			joinedload(Movement.user),
		)

		role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
		if role != "admin":
			query = query.filter(Movement.user_id == current_user.id)

		if year:
			start = datetime(year, month or 1, 1)
			if month:
				end = datetime(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
			else:
				end = datetime(year + 1, 1, 1)
			query = query.filter(Movement.fecha >= start, Movement.fecha < end)

		return query.order_by(Movement.fecha.desc()).all()
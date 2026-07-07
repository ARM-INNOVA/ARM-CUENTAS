import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Optional

import PyPDF2
import pdfplumber
from PIL import Image

from app.config import logger, settings

try:
	import pytesseract
except Exception:  # pragma: no cover - OCR opcional
	pytesseract = None


class InvoiceParser:
	"""Parseo básico de facturas con fallback seguro."""

	DATE_RE = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})")
	INVOICE_RE = re.compile(r"(?:factura|fra\.?|n[º°o]|invoice|ref\.?)[\s:#-]*([A-Z0-9./_-]+)", re.IGNORECASE)
	VAT_RE = re.compile(r"(\d{1,2})\s*%\s*(?:IVA)?", re.IGNORECASE)
	CIF_RE = re.compile(r"\b([A-HJNP-SUVW]\d{7}[0-9A-J]|\d{8}[A-Z]|[XYZ]\d{7}[A-Z])\b", re.IGNORECASE)

	@classmethod
	def parse_file(cls, file_path: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
		path = Path(file_path)
		text = ""

		if path.suffix.lower() == ".pdf":
			text = cls.extract_text_from_pdf(file_path)
			if cls._needs_ocr(text) and settings.USE_OCR:
				text = cls.extract_text_with_ocr(file_path) or text
		else:
			if settings.USE_OCR:
				text = cls.extract_text_with_ocr(file_path)

		data = cls.extract_invoice_data(text)
		data["texto_extraido"] = text[:12000]
		data["parser"] = "ocr" if path.suffix.lower() != ".pdf" and text else "pdf-text"
		data["necesita_revision"] = data.get("confianza", 0) < 70
		return data

	@staticmethod
	def extract_text_from_pdf(file_path: str) -> str:
		chunks = []
		try:
			with pdfplumber.open(file_path) as pdf:
				for page in pdf.pages:
					chunks.append(page.extract_text() or "")
		except Exception as exc:
			logger.warning("pdfplumber fallo en %s: %s", file_path, exc)

		text = "\n".join(chunks).strip()
		if text:
			return text

		try:
			with open(file_path, "rb") as file_handle:
				reader = PyPDF2.PdfReader(file_handle)
				return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
		except Exception as exc:
			logger.warning("PyPDF2 fallo en %s: %s", file_path, exc)
			return ""

	@staticmethod
	def extract_text_with_ocr(file_path: str) -> str:
		if not settings.USE_OCR or pytesseract is None:
			return ""

		try:
			with Image.open(file_path) as image:
				return pytesseract.image_to_string(image, lang="spa+eng").strip()
		except Exception as exc:
			logger.warning("OCR no disponible para %s: %s", file_path, exc)
			return ""

	@classmethod
	def extract_invoice_data(cls, text: str) -> Dict[str, Any]:
		data: Dict[str, Any] = {
			"fecha": None,
			"numero_factura": None,
			"proveedor": None,
			"nif_cif": None,
			"base_imponible": None,
			"iva_porcentaje": None,
			"iva_cantidad": None,
			"importe_total": None,
			"concepto": None,
			"confianza": 0,
		}

		if not text:
			return data

		lines = [line.strip() for line in text.splitlines() if line.strip()]
		lower_text = text.lower()

		date_match = cls.DATE_RE.search(text)
		if date_match:
			data["fecha"] = date_match.group(1)

		invoice_match = cls.INVOICE_RE.search(text)
		if invoice_match:
			data["numero_factura"] = invoice_match.group(1).strip(" .:-")

		cif_match = cls.CIF_RE.search(text)
		if cif_match:
			data["nif_cif"] = cif_match.group(1).upper()

		data["proveedor"] = cls._extract_supplier(lines)
		data["concepto"] = cls._extract_concept(lines)

		amounts = cls._extract_amounts(text)
		if amounts:
			data["importe_total"] = float(amounts[-1])
		if len(amounts) >= 2:
			data["iva_cantidad"] = float(amounts[-2])
		if len(amounts) >= 3:
			data["base_imponible"] = float(amounts[-3])

		vat_match = cls.VAT_RE.search(text)
		if vat_match:
			data["iva_porcentaje"] = int(vat_match.group(1))

		cls._normalize_tax_fields(data)
		data["tipo_detectado"] = "ingreso" if any(term in lower_text for term in ["factura emitida", "cliente", "abono", "venta"]) else "gasto"
		data["confianza"] = cls._score(data)
		return data

	@staticmethod
	def detect_invoice_type(text: str) -> str:
		text_lower = text.lower()
		if any(keyword in text_lower for keyword in ["factura emitida", "venta", "cliente"]):
			return "ingreso"
		return "gasto"

	@staticmethod
	def _needs_ocr(text: str) -> bool:
		return len((text or "").strip()) < 40

	@staticmethod
	def _extract_supplier(lines: list[str]) -> Optional[str]:
		for line in lines[:8]:
			if len(line) < 4:
				continue
			if any(token in line.lower() for token in ["factura", "fecha", "iva", "total", "base"]):
				continue
			return line[:120]
		return None

	@staticmethod
	def _extract_concept(lines: list[str]) -> Optional[str]:
		for line in lines:
			lowered = line.lower()
			if any(token in lowered for token in ["concepto", "descripcion", "detalle"]):
				parts = re.split(r":", line, maxsplit=1)
				return parts[-1].strip()[:200]
		return None

	@staticmethod
	def _extract_amounts(text: str) -> list[Decimal]:
		matches = re.findall(r"\d{1,3}(?:[.\s]\d{3})*(?:,\d{2})|\d+[.]\d{2}", text)
		amounts: list[Decimal] = []
		for match in matches:
			normalized = match.replace(" ", "").replace(".", "").replace(",", ".")
			try:
				amounts.append(Decimal(normalized))
			except InvalidOperation:
				continue
		return sorted(amounts)

	@staticmethod
	def _normalize_tax_fields(data: Dict[str, Any]) -> None:
		base = data.get("base_imponible")
		vat_amount = data.get("iva_cantidad")
		vat_pct = data.get("iva_porcentaje")
		total = data.get("importe_total")

		if base and vat_pct and not vat_amount:
			data["iva_cantidad"] = round(float(Decimal(str(base)) * Decimal(str(vat_pct)) / Decimal("100")), 2)
		if base and vat_amount and not total:
			data["importe_total"] = round(float(Decimal(str(base)) + Decimal(str(vat_amount))), 2)
		if total and vat_amount and not base:
			data["base_imponible"] = round(float(Decimal(str(total)) - Decimal(str(vat_amount))), 2)
		if base and vat_amount and not vat_pct and float(base) != 0:
			calculated = round((float(vat_amount) / float(base)) * 100)
			if calculated in {4, 10, 21}:
				data["iva_porcentaje"] = calculated

	@staticmethod
	def _score(data: Dict[str, Any]) -> int:
		score = 0
		for key in ["fecha", "numero_factura", "proveedor", "importe_total", "base_imponible", "iva_porcentaje"]:
			if data.get(key) not in (None, ""):
				score += 15
		if data.get("nif_cif"):
			score += 10
		return min(score, 100)
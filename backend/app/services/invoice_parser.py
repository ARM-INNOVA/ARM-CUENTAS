import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional

import PyPDF2
import pdfplumber
from PIL import Image

from app.config import logger, settings

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None


class InvoiceParser:
    DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]+\s+\d{4})\b")
    CIF_RE = re.compile(r"\b([A-HJNP-SUVW]\d{7}[0-9A-J]|\d{8}[A-Z]|[XYZ]\d{7}[A-Z])\b", re.IGNORECASE)
    AMOUNT_RE = re.compile(r"(?<!\d)(?:\d{1,3}(?:[.\s]\d{3})+|\d+)(?:[.,]\d{2})?(?!\d)")

    PROVIDERS = {
        "saltoki": ["SALTOKI"],
        "ballenoil": ["BALLENOIL"],
        "obramat": ["OBRAMAT", "BRICOLAJE BRICOMAN"],
        "brico_depot": ["BRICO DEPOT", "BRICODEPOT", "EURO DEPOT"],
        "leroy_merlin": ["LEROY MERLIN"],
    }

    @classmethod
    def parse_file(cls, file_path: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
        path = Path(file_path)
        warnings: List[str] = []
        pages: List[str] = []

        if path.suffix.lower() == ".pdf":
            pages = cls.extract_text_pages_from_pdf(file_path)
            if cls._needs_ocr("\n".join(pages)):
                warnings.append("Este PDF no contiene texto seleccionable. OCR avanzado pendiente o desactivado.")
        elif settings.USE_OCR:
            pages = [cls.extract_text_with_ocr(file_path)]

        full_text = "\n".join([p for p in pages if p]).strip()
        provider_key = cls.detect_provider(full_text)

        data = cls._base_result()
        data["warnings"] = warnings.copy()
        data["extracted_text"] = full_text[:20000]

        parser_map = {
            "saltoki": cls._parse_saltoki,
            "ballenoil": cls._parse_ballenoil,
            "obramat": cls._parse_obramat,
            "brico_depot": cls._parse_brico_depot,
            "leroy_merlin": cls._parse_leroy_merlin,
            "generic": cls._parse_generic,
        }
        parser = parser_map.get(provider_key, cls._parse_generic)
        parsed = parser(full_text, pages)
        data.update(parsed)

        cls._normalize_result(data)
        cls._validate_accounting(data)

        required = ["supplier_name", "invoice_number", "invoice_date", "tax_base", "vat_amount", "total_amount"]
        data["needs_review"] = any(data.get(key) in (None, "") for key in required) or len(data["warnings"]) > 0
        data["confidence"] = cls._compute_confidence(data)

        # Compatibilidad con estructura existente del proyecto.
        data["fecha"] = data.get("sale_date") or data.get("invoice_date")
        data["numero_factura"] = data.get("invoice_number")
        data["proveedor"] = data.get("supplier_name")
        data["nif_cif"] = data.get("supplier_tax_id")
        data["base_imponible"] = data.get("tax_base")
        data["iva_porcentaje"] = data.get("vat_rate")
        data["iva_cantidad"] = data.get("vat_amount")
        data["importe_total"] = data.get("total_amount")
        data["texto_extraido"] = data.get("extracted_text")
        data["confianza"] = int(round((data.get("confidence") or 0) * 100))
        data["necesita_revision"] = data.get("needs_review", True)
        data["tipo_detectado"] = "gasto"

        return data

    @classmethod
    def parse_text(cls, text: str) -> Dict[str, Any]:
        data = cls._base_result()
        provider_key = cls.detect_provider(text)
        parser_map = {
            "saltoki": cls._parse_saltoki,
            "ballenoil": cls._parse_ballenoil,
            "obramat": cls._parse_obramat,
            "brico_depot": cls._parse_brico_depot,
            "leroy_merlin": cls._parse_leroy_merlin,
            "generic": cls._parse_generic,
        }
        parser = parser_map.get(provider_key, cls._parse_generic)
        parsed = parser(text, [text])
        data.update(parsed)
        data["extracted_text"] = text[:20000]
        cls._normalize_result(data)
        cls._validate_accounting(data)
        required = ["supplier_name", "invoice_number", "invoice_date", "tax_base", "vat_amount", "total_amount"]
        data["needs_review"] = any(data.get(key) in (None, "") for key in required) or len(data.get("warnings", [])) > 0
        data["confidence"] = cls._compute_confidence(data)
        return data

    @staticmethod
    def _base_result() -> Dict[str, Any]:
        return {
            "supplier_name": "",
            "supplier_tax_id": "",
            "invoice_number": "",
            "invoice_date": "",
            "sale_date": "",
            "tax_base": None,
            "vat_rate": None,
            "vat_amount": None,
            "total_amount": None,
            "payment_method": "",
            "needs_review": True,
            "confidence": 0,
            "warnings": [],
            "extracted_text": "",
            "field_sources": {},
        }

    @classmethod
    def extract_text_pages_from_pdf(cls, file_path: str) -> List[str]:
        pages: List[str] = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    pages.append((page.extract_text() or "").strip())
        except Exception as exc:
            logger.warning("pdfplumber fallo en %s: %s", file_path, exc)

        if any(pages):
            return pages

        try:
            with open(file_path, "rb") as file_handle:
                reader = PyPDF2.PdfReader(file_handle)
                return [((page.extract_text() or "").strip()) for page in reader.pages]
        except Exception as exc:
            logger.warning("PyPDF2 fallo en %s: %s", file_path, exc)
            return []

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
    def detect_provider(cls, text: str) -> str:
        upper = (text or "").upper()
        for key, markers in cls.PROVIDERS.items():
            if any(marker in upper for marker in markers):
                return key
        return "generic"

    @classmethod
    def _parse_generic(cls, text: str, pages: List[str]) -> Dict[str, Any]:
        result = cls._base_result()
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        result["supplier_name"] = cls._extract_supplier(lines)
        result["supplier_tax_id"] = cls._extract_tax_id(text) or ""
        result["invoice_number"] = cls._extract_invoice_number(text) or ""
        result["invoice_date"] = cls._extract_date_with_label(text, ["fecha factura", "fecha"]) or cls._extract_first_date(text) or ""
        result["sale_date"] = cls._extract_date_with_label(text, ["fecha venta", "fecha de venta", "operacion"]) or ""

        result["tax_base"] = cls._extract_amount_by_labels(text, ["base imponible", "base"], avoid=["cambio", "efectivo"])
        result["vat_amount"] = cls._extract_amount_by_labels(text, ["cuota iva", "importe iva", "iva"], avoid=["%"])
        result["total_amount"] = cls._extract_total_amount(text)
        result["vat_rate"] = cls._extract_vat_rate(text)
        result["payment_method"] = cls._extract_payment_method(text) or ""

        result["field_sources"] = {
            "tax_base": "Detectado en texto por etiquetas de base" if result["tax_base"] is not None else "Pendiente de revisar",
            "vat_amount": "Detectado en texto por etiquetas de IVA" if result["vat_amount"] is not None else "Pendiente de revisar",
            "total_amount": "Detectado por contexto de total" if result["total_amount"] is not None else "Pendiente de revisar",
        }
        return result

    @classmethod
    def _parse_saltoki(cls, text: str, pages: List[str]) -> Dict[str, Any]:
        result = cls._parse_generic(text, pages)
        result["supplier_name"] = cls._find_first_match(text, [r"SALTOKI[^\n]*"]) or "SALTOKI"
        result["supplier_tax_id"] = cls._extract_tax_id(text) or result["supplier_tax_id"]
        numero_line = cls._find_first_match(text, [r"CLIENTE\s*/\s*FECHA\s*/\s*N[ÚU]MERO[^\n]*", r"N[ÚU]MERO[^\n]*"]) or ""
        numero_tokens = re.findall(r"\d{3,}", numero_line)
        if numero_tokens:
            result["invoice_number"] = numero_tokens[-1]
        else:
            result["invoice_number"] = cls._extract_with_regex(text, [r"FACTURA\s*[:#]?\s*(\d{3,})"]) or result["invoice_number"]
        result["invoice_date"] = cls._extract_date_with_label(text, ["fecha", "cliente / fecha / número", "cliente/fecha/número"]) or result["invoice_date"]

        table = cls._extract_vat_table_row(text, label_patterns=["base imponible", "% i.v.a", "i.v.a.", "total"])
        if table:
            result["tax_base"] = table.get("base")
            result["vat_rate"] = table.get("rate") or result["vat_rate"]
            result["vat_amount"] = table.get("vat")
            result["total_amount"] = table.get("total")
            result["field_sources"]["total_amount"] = "Detectado en tabla resumen de Saltoki"
        return result

    @classmethod
    def _parse_ballenoil(cls, text: str, pages: List[str]) -> Dict[str, Any]:
        # Ballenoil: priorizar primera pagina para evitar bono de lavado de pagina 2.
        first_page = pages[0] if pages else text
        result = cls._parse_generic(first_page, [first_page])
        result["supplier_name"] = "BALLENOIL, S.A."
        result["supplier_tax_id"] = cls._extract_tax_id(first_page) or result["supplier_tax_id"]
        result["invoice_number"] = cls._extract_with_regex(first_page, [r"(FRA/\d+)", r"FACTURA\s*[:#]?\s*([A-Z0-9/-]+)"]) or result["invoice_number"]
        result["invoice_date"] = cls._extract_date_with_label(first_page, ["fecha factura", "fecha"]) or result["invoice_date"]
        result["vat_rate"] = cls._extract_vat_rate(first_page) or result["vat_rate"]
        result["tax_base"] = cls._extract_amount_by_labels(first_page, ["base imponible"], avoid=["litros", "precio"]) or result["tax_base"]
        result["vat_amount"] = cls._extract_amount_after_labels(first_page, ["iva", "cuota iva"]) or result["vat_amount"]
        result["total_amount"] = cls._extract_amount_after_labels(first_page, ["total factura", "importe total", "total a pagar", "total"]) or result["total_amount"]
        result["field_sources"]["total_amount"] = "Detectado en pagina 1 Ballenoil"
        return result

    @classmethod
    def _parse_obramat(cls, text: str, pages: List[str]) -> Dict[str, Any]:
        result = cls._parse_generic(text, pages)
        result["supplier_name"] = cls._find_first_match(text, [r"BRICOLAJE BRICOMAN[^\n]*", r"OBRAMAT[^\n]*"]) or "OBRAMAT"
        result["invoice_number"] = cls._extract_with_regex(text, [r"(\d{3}-\d{4}-\d{6})", r"FACTURA\s*[:#]?\s*([A-Z0-9/-]+)"]) or result["invoice_number"]
        result["invoice_date"] = cls._extract_date_with_label(text, ["fecha", "fecha factura"]) or result["invoice_date"]

        # OBRAMAT: usar siempre la tabla resumen inferior para totales contables.
        # Evita tomar importes de lineas de producto, efectivo o cambio.
        summary = cls._extract_obramat_summary(text)
        if summary:
            result["vat_rate"] = summary["vat_rate"]
            result["tax_base"] = summary["tax_base"]
            result["vat_amount"] = summary["vat_amount"]
            result["total_amount"] = summary["total_amount"]
            result["field_sources"]["tax_base"] = "Detectado en tabla resumen OBRAMAT"
            result["field_sources"]["vat_amount"] = "Detectado en tabla resumen OBRAMAT"
            result["field_sources"]["total_amount"] = "Detectado en tabla resumen OBRAMAT"
            return result

        # Fallback controlado: si no hay resumen, mantener parser generico pero forzar revision.
        result["warnings"].append("No se detecto tabla resumen OBRAMAT. Revisar importes manualmente.")
        return result

    @classmethod
    def _extract_obramat_summary(cls, text: str) -> Optional[Dict[str, float]]:
        lower = text.lower()
        anchors = ["tasa iva/igic/ipsi", "total", "total iva", "total tti"]
        anchor_positions = [lower.rfind(anchor) for anchor in anchors]
        valid_positions = [pos for pos in anchor_positions if pos != -1]
        if not valid_positions:
            return None

        start = min(valid_positions)
        zone = text[start:]
        lines = [line.strip() for line in zone.splitlines() if line.strip()]

        amount_token = r"(?:\d{1,3}(?:[.\s]\d{3})*|\d+)[.,]\d{2}"
        pattern = re.compile(
            rf"(?P<vat_rate>\d{{1,2}}(?:[.,]\d{{1,2}})?%?)\s+"
            rf"(?P<tax_base>{amount_token})\s+"
            rf"(?P<vat_amount>{amount_token})\s+"
            rf"(?P<total_amount>{amount_token})"
        )

        for line in lines:
            lowered = line.lower()
            if any(token in lowered for token in ["efectivo", "cambio", "precio", "linea"]):
                continue

            match = pattern.search(line)
            if not match:
                continue

            vat_raw = match.group("vat_rate").replace("%", "").strip()
            vat_rate = cls._normalize_amount(vat_raw)
            tax_base = cls._normalize_amount(match.group("tax_base"), require_decimals=True)
            vat_amount = cls._normalize_amount(match.group("vat_amount"), require_decimals=True)
            total_amount = cls._normalize_amount(match.group("total_amount"), require_decimals=True)

            if None in (vat_rate, tax_base, vat_amount, total_amount):
                continue

            if float(total_amount) <= float(tax_base):
                continue

            return {
                "vat_rate": int(round(float(vat_rate))),
                "tax_base": round(float(tax_base), 2),
                "vat_amount": round(float(vat_amount), 2),
                "total_amount": round(float(total_amount), 2),
            }

        return None

    @classmethod
    def _parse_brico_depot(cls, text: str, pages: List[str]) -> Dict[str, Any]:
        result = cls._parse_generic(text, pages)
        result["supplier_name"] = cls._find_first_match(text, [r"EURO DEPOT[^\n]*", r"BRICO\s*DEP[ÔO]T[^\n]*"]) or "Brico Depot"
        result["invoice_number"] = cls._extract_with_regex(text, [r"(FT\s*\d+/\d+)", r"N[º°o]?\s*FACTURA\s*[:#]?\s*([A-Z0-9 /.-]+)"]) or result["invoice_number"]
        result["invoice_date"] = cls._extract_date_with_label(text, ["fecha", "fecha factura"]) or result["invoice_date"]

        block = cls._extract_block(text, ["base", "cuota", "recargo", "total"])
        if block:
            summary_values = cls._extract_summary_values(block, ["base", "cuota", "total"])
            if summary_values:
                result["tax_base"] = summary_values["base"]
                result["vat_amount"] = summary_values["vat"]
                result["total_amount"] = summary_values["total"]
                result["field_sources"]["total_amount"] = "Detectado en tabla Base/Cuota/Recargo/Total"

        result["vat_rate"] = cls._extract_vat_rate(block or text) or result["vat_rate"]
        return result

    @classmethod
    def _parse_leroy_merlin(cls, text: str, pages: List[str]) -> Dict[str, Any]:
        result = cls._parse_generic(text, pages)
        result["supplier_name"] = cls._find_first_match(text, [r"LEROY MERLIN[^\n]*"]) or "Leroy Merlin"
        result["invoice_number"] = cls._extract_with_regex(text, [r"(\d{3}-\d{4}-\d{6})", r"FACTURA\s*[:#]?\s*([A-Z0-9/-]+)"]) or result["invoice_number"]

        sale_date = cls._extract_date_with_label(text, ["fecha de venta", "fecha venta"])
        result["sale_date"] = sale_date or result["sale_date"]
        result["invoice_date"] = sale_date or cls._extract_date_with_label(text, ["fecha de emisión", "fecha emision", "fecha"]) or result["invoice_date"]

        result["tax_base"] = cls._extract_amount_by_labels(text, ["base imponible", "base"], avoid=["total"]) or result["tax_base"]
        result["vat_amount"] = cls._extract_amount_after_labels(text, ["cuota iva", "iva"]) or result["vat_amount"]
        result["total_amount"] = cls._extract_amount_after_labels(text, ["total factura", "importe total", "total"]) or result["total_amount"]
        result["vat_rate"] = cls._extract_vat_rate(text) or result["vat_rate"]
        result["field_sources"]["invoice_date"] = "Fecha de venta priorizada" if sale_date else "Fecha de emisión usada"
        return result

    @classmethod
    def _normalize_result(cls, data: Dict[str, Any]) -> None:
        for key in ["supplier_name", "supplier_tax_id", "invoice_number", "invoice_date", "sale_date", "payment_method"]:
            if data.get(key) is None:
                data[key] = ""
            if isinstance(data.get(key), str):
                data[key] = data[key].strip()

        for key in ["tax_base", "vat_amount", "total_amount"]:
            if data.get(key) is not None:
                data[key] = round(float(data[key]), 2)

        if data.get("vat_rate") is not None:
            try:
                data["vat_rate"] = int(data["vat_rate"])
            except (TypeError, ValueError):
                data["vat_rate"] = None

    @classmethod
    def _validate_accounting(cls, data: Dict[str, Any]) -> None:
        base = data.get("tax_base")
        vat = data.get("vat_amount")
        total = data.get("total_amount")
        if base is None or vat is None or total is None:
            return

        expected = round(float(Decimal(str(base)) + Decimal(str(vat))), 2)
        diff = abs(expected - float(total))
        if diff > 0.02:
            data["warnings"].append("Base + IVA no coincide con total")

    @classmethod
    def _compute_confidence(cls, data: Dict[str, Any]) -> float:
        keys = [
            "supplier_name",
            "supplier_tax_id",
            "invoice_number",
            "invoice_date",
            "tax_base",
            "vat_rate",
            "vat_amount",
            "total_amount",
        ]
        hit = sum(1 for key in keys if data.get(key) not in (None, ""))
        return round(hit / len(keys), 2)

    @classmethod
    def _extract_supplier(cls, lines: List[str]) -> str:
        for line in lines[:12]:
            lower = line.lower()
            if len(line) < 4:
                continue
            if any(token in lower for token in ["factura", "fecha", "base", "total", "iva", "cliente"]):
                continue
            return line[:120]
        return ""

    @classmethod
    def _extract_tax_id(cls, text: str) -> Optional[str]:
        match = cls.CIF_RE.search(text)
        return match.group(1).upper() if match else None

    @classmethod
    def _extract_invoice_number(cls, text: str) -> Optional[str]:
        return cls._extract_with_regex(
            text,
            [
                r"(?:N[º°o]?\s*FACTURA|FACTURA|FRA)\s*[:#-]?\s*([A-Z0-9./_-]{3,})",
                r"\b([A-Z]{1,4}/\d{4,})\b",
                r"\b(\d{3}-\d{4}-\d{6})\b",
            ],
        )

    @classmethod
    def _extract_first_date(cls, text: str) -> Optional[str]:
        for raw in cls.DATE_RE.findall(text):
            normalized = cls._normalize_date(raw)
            if normalized:
                return normalized
        return None

    @classmethod
    def _extract_date_with_label(cls, text: str, labels: List[str]) -> Optional[str]:
        lower = text.lower()
        for label in labels:
            idx = lower.find(label.lower())
            if idx == -1:
                continue
            window = text[idx: idx + 120]
            for raw in cls.DATE_RE.findall(window):
                normalized = cls._normalize_date(raw)
                if normalized:
                    return normalized
        return None

    @staticmethod
    def _normalize_date(raw: str) -> Optional[str]:
        raw_clean = " ".join(raw.strip().split())
        formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
        for fmt in formats:
            try:
                return datetime.strptime(raw_clean, fmt).date().isoformat()
            except ValueError:
                continue

        month_map = {
            "enero": "01",
            "febrero": "02",
            "marzo": "03",
            "abril": "04",
            "mayo": "05",
            "junio": "06",
            "julio": "07",
            "agosto": "08",
            "septiembre": "09",
            "setiembre": "09",
            "octubre": "10",
            "noviembre": "11",
            "diciembre": "12",
        }
        m = re.match(r"^(\d{1,2})\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+)\s+(\d{4})$", raw_clean)
        if not m:
            return None
        day, month_name, year = m.groups()
        month = month_map.get(month_name.lower())
        if not month:
            return None
        try:
            return datetime(int(year), int(month), int(day)).date().isoformat()
        except ValueError:
            return None

    @classmethod
    def _extract_vat_rate(cls, text: str) -> Optional[int]:
        rates = [int(x) for x in re.findall(r"\b(21|10|4)\s*%", text)]
        if not rates:
            return None
        if 21 in rates:
            return 21
        if 10 in rates:
            return 10
        return 4

    @classmethod
    def _extract_payment_method(cls, text: str) -> Optional[str]:
        lower = text.lower()
        for token in ["tarjeta", "transferencia", "bizum", "efectivo"]:
            if token in lower:
                return token
        return None

    @classmethod
    def _extract_total_amount(cls, text: str) -> Optional[float]:
        value = cls._extract_amount_by_labels(
            text,
            ["total factura", "importe total", "total a pagar", "total tti", "total tii", "total eur", "total"],
            avoid=["efectivo", "cambio", "articulo", "ud", "precio"],
        )
        if value is not None:
            return value
        return None

    @classmethod
    def _extract_amount_by_labels(cls, text: str, labels: List[str], avoid: Optional[List[str]] = None) -> Optional[float]:
        avoid = avoid or []
        best: Optional[Decimal] = None
        best_score = -1
        lower = text.lower()

        for match in cls.AMOUNT_RE.finditer(text):
            raw = match.group(0)
            amount = cls._normalize_amount(raw, require_decimals=True)
            if amount is None:
                continue
            start = max(match.start() - 60, 0)
            end = min(match.end() + 60, len(text))
            context = lower[start:end]
            score = 0
            if any(label.lower() in context for label in labels):
                score += 5
            if any(word.lower() in context for word in avoid):
                score -= 8
            if "%" in context and any(label.lower() == "iva" for label in labels):
                score -= 2
            if amount >= Decimal("1"):
                score += 1

            if score > best_score:
                best_score = score
                best = amount

        if best is None or best_score < 0:
            return None
        return round(float(best), 2)

    @classmethod
    def _extract_amount_after_labels(cls, text: str, labels: List[str]) -> Optional[float]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            lower = line.lower()
            if not any(label.lower() in lower for label in labels):
                continue
            values = cls._extract_numbers_from_line(line)
            if not values:
                continue
            return round(float(values[-1]), 2)
        return None

    @classmethod
    def _extract_vat_table_row(cls, text: str, label_patterns: List[str]) -> Optional[Dict[str, Any]]:
        if not all(pattern.lower() in text.lower() for pattern in label_patterns):
            return None

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for i, line in enumerate(lines):
            lower = line.lower()
            normalized = re.sub(r"[^a-z0-9\s]", "", lower)
            if "base" in normalized and "iva" in normalized and "total" in normalized:
                for row in lines[i + 1:i + 4]:
                    numbers = cls._extract_numbers_from_line(row)
                    if len(numbers) >= 3:
                        rate = cls._extract_vat_rate(row)
                        if len(numbers) >= 4:
                            base, vat, total = numbers[0], numbers[2], numbers[3]
                        else:
                            base, vat, total = numbers[0], numbers[1], numbers[2]
                        return {
                            "base": round(float(base), 2),
                            "rate": rate,
                            "vat": round(float(vat), 2),
                            "total": round(float(total), 2),
                        }
        return None

    @classmethod
    def _extract_numbers_from_line(cls, line: str) -> List[Decimal]:
        nums: List[Decimal] = []
        for token in cls.AMOUNT_RE.findall(line):
            value = cls._normalize_amount(token, require_decimals=True)
            if value is not None:
                nums.append(value)
        return nums

    @classmethod
    def _extract_summary_values(cls, text: str, header_keywords: List[str]) -> Optional[Dict[str, float]]:
        lower = text.lower()
        if not all(k in lower for k in header_keywords):
            return None

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            candidate = " ".join(lines[idx: idx + 3]).lower()
            if not all(k in candidate for k in header_keywords):
                continue

            for row in lines[idx + 1: idx + 5]:
                numbers = cls._extract_numbers_from_line(row)
                if len(numbers) < 3:
                    continue
                if len(numbers) >= 4:
                    monetary = [numbers[0], numbers[1], numbers[3]]
                else:
                    monetary = [numbers[0], numbers[1], numbers[2]]
                return {
                    "base": round(float(monetary[0]), 2),
                    "vat": round(float(monetary[1]), 2),
                    "total": round(float(monetary[2]), 2),
                }
        return None

    @classmethod
    def _extract_block(cls, text: str, contains: List[str]) -> str:
        lines = [line for line in text.splitlines()]
        lower_needles = [c.lower() for c in contains]
        for idx, line in enumerate(lines):
            window = "\n".join(lines[idx: idx + 8]).lower()
            if all(n in window for n in lower_needles):
                return "\n".join(lines[idx: idx + 8])
        return ""

    @staticmethod
    def _extract_with_regex(text: str, patterns: List[str]) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip(" .:-")
                if value:
                    return value
        return None

    @staticmethod
    def _find_first_match(text: str, patterns: List[str]) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(0).strip()
                if value:
                    return value
        return None

    @staticmethod
    def _normalize_amount(raw: str, require_decimals: bool = False) -> Optional[Decimal]:
        value = raw.replace("€", "").replace(" ", "")
        if not value:
            return None

        if require_decimals and not ("," in value or "." in value):
            return None

        if "," in value and "." in value:
            normalized = value.replace(".", "").replace(",", ".")
        elif "," in value:
            normalized = value.replace(",", ".")
        elif "." in value:
            parts = value.split(".")
            if len(parts) == 2 and len(parts[1]) == 2:
                normalized = value
            else:
                normalized = value.replace(".", "")
        else:
            normalized = value

        try:
            parsed = Decimal(normalized)
            if require_decimals and parsed >= Decimal("100000"):
                return None
            return parsed
        except InvalidOperation:
            return None

    @staticmethod
    def _needs_ocr(text: str) -> bool:
        return len((text or "").strip()) < 40

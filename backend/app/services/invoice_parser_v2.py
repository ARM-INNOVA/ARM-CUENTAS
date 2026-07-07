import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber

from app.config import logger
from app.services.invoice_parser import InvoiceParser as LegacyInvoiceParser


class InvoiceParserV2:
    AMOUNT_RE = re.compile(r"(?<!\d)(?:\d{1,3}(?:[.\s]\d{3})*|\d+)(?:[.,]\d{2})(?!\d)")
    DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})\b")

    @classmethod
    def parse_file(cls, file_path: str, mime_type: Optional[str] = None) -> Dict[str, Any]:
        text = cls._extract_pdf_text(file_path) if Path(file_path).suffix.lower() == ".pdf" else ""
        if not text:
            parsed = cls.parse_text("")
            parsed["warnings"].append("No se pudo extraer texto del archivo.")
            parsed["needs_review"] = True
            return parsed
        return cls.parse_text(text)

    @classmethod
    def parse_text(cls, text: str) -> Dict[str, Any]:
        provider_key = cls._detect_provider(text)

        if provider_key == "ballenoil":
            result = cls.parse_ballenoil(text)
        elif provider_key == "bricodepot":
            result = cls.parse_bricodepot(text)
        elif provider_key == "leroy":
            result = cls.parse_leroy_merlin(text)
        else:
            legacy = LegacyInvoiceParser.parse_text(text)
            result = cls._base_result()
            result.update(
                {
                    "supplier_name": legacy.get("supplier_name", ""),
                    "supplier_tax_id": legacy.get("supplier_tax_id", ""),
                    "invoice_number": legacy.get("invoice_number", ""),
                    "invoice_date": legacy.get("invoice_date", ""),
                    "sale_date": legacy.get("sale_date", ""),
                    "tax_base": legacy.get("tax_base"),
                    "vat_rate": legacy.get("vat_rate"),
                    "vat_amount": legacy.get("vat_amount"),
                    "total_amount": legacy.get("total_amount"),
                    "payment_method": legacy.get("payment_method", ""),
                    "needs_review": legacy.get("needs_review", True),
                    "confidence": legacy.get("confidence", 0),
                    "warnings": legacy.get("warnings", []),
                    "extracted_text": (text or "")[:20000],
                }
            )

        cls._add_compat_aliases(result)
        return result

    @classmethod
    def parse_ballenoil(cls, text: str) -> Dict[str, Any]:
        data = cls._base_result()
        data["supplier_name"] = "BALLENOIL, S.A."
        data["invoice_number"] = cls._extract_regex(text, [r"(FRA/\d+)"]) or ""
        data["invoice_date"] = cls._extract_date_with_label(text, ["fecha factura", "fecha"]) or ""

        # Resumen obligatorio: base imponible, importe iva y total factura.
        summary_zone = cls._slice_from_keywords(text, ["base imponible", "importe iva", "total factura", "iva", "total"])

        data["tax_base"] = cls._extract_amount_after_label(summary_zone, ["base imponible"]) or cls._extract_amount_after_label(summary_zone, ["base"])
        data["vat_amount"] = cls._extract_amount_after_label(summary_zone, ["importe iva", "cuota iva", "iva"])
        data["total_amount"] = cls._extract_amount_after_label(summary_zone, ["total factura", "importe total", "total"])
        data["vat_rate"] = cls._extract_percentage(summary_zone, ["iva"]) or 10

        if data["tax_base"] is None or data["vat_amount"] is None or data["total_amount"] is None:
            # Fallback linealizado del resumen (162.43 / 10% 16.24 / 178.67)
            row_amounts = cls.extract_summary_line_amounts(
                summary_zone,
                keywords=["base imponible", "importe iva", "total factura", "iva", "total"],
            )
            if len(row_amounts) >= 3:
                data["tax_base"] = data["tax_base"] or row_amounts[0]
                data["vat_amount"] = data["vat_amount"] or row_amounts[1]
                data["total_amount"] = data["total_amount"] or row_amounts[2]

        if data["vat_rate"] is None and data["tax_base"] and data["vat_amount"]:
            data["vat_rate"] = cls._calc_rate(data["tax_base"], data["vat_amount"])

        cls._finalize(data)
        cls._log_parser_result("ballenoil", data)
        return data

    @classmethod
    def parse_bricodepot(cls, text: str) -> Dict[str, Any]:
        data = cls._base_result()
        data["supplier_name"] = "Euro Depot España S.A.U."
        data["supplier_tax_id"] = "A62018064"
        data["invoice_number"] = cls._extract_regex(text, [r"(FT\s*\d+/\d+)"]) or ""
        data["invoice_date"] = cls._extract_date_with_label(text, ["fecha", "nº factura"]) or ""

        summary_zone = cls._slice_from_keywords(text, ["base cuota recargo total", "total eur", "total", "base", "cuota", "recargo"])

        # Prioridad absoluta a la linea de resumen fiscal.
        lines = [line.strip() for line in summary_zone.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            ll = line.lower()
            if "base" in ll and "cuota" in ll and "recargo" in ll and "total" in ll:
                for row in lines[idx + 1: idx + 5]:
                    amounts = cls._extract_line_amounts(row)
                    if len(amounts) < 4:
                        continue
                    data["tax_base"] = amounts[0]
                    data["vat_amount"] = amounts[1]
                    data["total_amount"] = amounts[-1]
                    rate_match = re.search(r"(\d{1,2}(?:[.,]\d{1,2})?)\s*%", row)
                    if rate_match:
                        rate_value = cls._norm_amount(rate_match.group(1))
                        if rate_value is not None:
                            data["vat_rate"] = int(round(rate_value))
                    break
                break

        if data["total_amount"] is None:
            data["total_amount"] = cls._extract_amount_after_label(summary_zone, ["total eur", "total"]) 
        if data["tax_base"] is None:
            data["tax_base"] = cls._extract_amount_after_label(summary_zone, ["base"])
        if data["vat_amount"] is None:
            data["vat_amount"] = cls._extract_amount_after_label(summary_zone, ["cuota", "iva"])
        if data["vat_rate"] is None:
            data["vat_rate"] = cls._extract_percentage(summary_zone, ["base", "cuota", "iva"]) or cls._calc_rate(data["tax_base"], data["vat_amount"])

        cls._finalize(data)
        cls._log_parser_result("bricodepot", data)
        return data

    @classmethod
    def parse_leroy_merlin(cls, text: str) -> Dict[str, Any]:
        data = cls._base_result()
        data["supplier_name"] = "Leroy Merlin España S.L.U."
        data["supplier_tax_id"] = "B84818442"
        data["invoice_number"] = cls._extract_regex(text, [r"(\d{3}-\d{4}-\d{6})"]) or ""
        sale_date = cls._extract_date_with_label(text, ["fecha de venta", "fecha venta"])
        data["sale_date"] = sale_date or ""
        data["invoice_date"] = sale_date or cls._extract_date_with_label(text, ["fecha"]) or ""

        summary_zone = cls._slice_from_keywords(text, ["tasa iva/igic/ipsi", "total tti", "total tii", "total iva", "eur"])

        summary_row = cls._extract_regex(
            summary_zone,
            [
                r"(\d{1,2}(?:[.,]\d{1,2})?)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)",
                r"eur\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)",
            ],
            return_match=True,
        )

        if summary_row:
            groups = summary_row.groups()
            if len(groups) == 4:
                data["vat_rate"] = int(round(float(cls._norm_amount(groups[0]) or 0)))
                data["tax_base"] = cls._norm_amount(groups[1])
                data["vat_amount"] = cls._norm_amount(groups[2])
                data["total_amount"] = cls._norm_amount(groups[3])
            elif len(groups) == 3:
                data["tax_base"] = cls._norm_amount(groups[0])
                data["vat_amount"] = cls._norm_amount(groups[1])
                data["total_amount"] = cls._norm_amount(groups[2])

        if data["total_amount"] is None:
            data["total_amount"] = cls._extract_amount_after_label(summary_zone, ["total tti", "total tii", "importe tti", "total factura"])
        if data["tax_base"] is None:
            data["tax_base"] = cls._extract_amount_after_label(summary_zone, ["total si", "base"])
        if data["vat_amount"] is None:
            data["vat_amount"] = cls._extract_amount_after_label(summary_zone, ["total iva", "cuota iva", "iva"])
        if data["vat_rate"] is None:
            data["vat_rate"] = cls._extract_percentage(summary_zone, ["iva"]) or cls._calc_rate(data["tax_base"], data["vat_amount"])

        cls._finalize(data)
        cls._log_parser_result("leroy_merlin", data)
        return data

    @classmethod
    def extract_summary_line_amounts(cls, text: str, keywords: List[str]) -> List[float]:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        if not lines:
            return []

        keyword_lines = []
        lower_keywords = [k.lower() for k in keywords]
        for idx, line in enumerate(lines):
            ll = line.lower()
            if any(k in ll for k in lower_keywords):
                keyword_lines.append(idx)

        candidate_indexes = set()
        if keyword_lines:
            for idx in keyword_lines:
                for delta in (-1, 0, 1, 2):
                    pos = idx + delta
                    if 0 <= pos < len(lines):
                        candidate_indexes.add(pos)
        else:
            start = max(len(lines) - 8, 0)
            candidate_indexes.update(range(start, len(lines)))

        scored: List[tuple[int, List[float]]] = []
        for idx in sorted(candidate_indexes):
            line = lines[idx]
            ll = line.lower()
            if cls._line_looks_like_non_summary(ll):
                continue
            amounts = cls._extract_line_amounts(line)
            if not amounts:
                continue
            score = 0
            if any(k in ll for k in ["total factura", "total eur", "total tti", "total tii", "base cuota recargo total"]):
                score += 5
            if "base" in ll:
                score += 2
            if "iva" in ll:
                score += 2
            scored.append((score, amounts))

        if not scored:
            return []

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    @classmethod
    def _extract_pdf_text(cls, file_path: str) -> str:
        chunks: List[str] = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    chunks.append(page.extract_text() or "")
        except Exception:
            return ""
        return "\n".join(chunks).strip()

    @classmethod
    def _detect_provider(cls, text: str) -> str:
        upper = (text or "").upper()
        if "BALLENOIL" in upper:
            return "ballenoil"
        if any(token in upper for token in ["EURO DEPOT", "BRICO DEPOT", "BRICODEPOT", "BRICODEPOT.ES", "BRICO DEPÔT"]):
            return "bricodepot"
        if "LEROY MERLIN" in upper:
            return "leroy"
        return "generic"

    @classmethod
    def _extract_line_amounts(cls, line: str) -> List[float]:
        amounts: List[float] = []
        for m in cls.AMOUNT_RE.finditer(line):
            suffix = line[m.end(): m.end() + 8].lower().strip()
            prefix = line[max(0, m.start() - 10): m.start()].lower()
            token = m.group(0)

            if suffix.startswith("l") or "litro" in suffix:
                continue
            if re.search(r"\d\s*l\b", line.lower()):
                continue
            if cls._is_unit_price_context(prefix, suffix):
                continue

            value = cls._norm_amount(token)
            if value is not None:
                amounts.append(value)
        return amounts

    @classmethod
    def _extract_amount_after_label(cls, text: str, labels: List[str]) -> Optional[float]:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        for line in lines:
            ll = line.lower()
            if not any(label.lower() in ll for label in labels):
                continue
            if cls._line_looks_like_non_summary(ll) and "total" not in ll and "base" not in ll and "iva" not in ll:
                continue
            values = cls._extract_line_amounts(line)
            if values:
                return values[-1]
        return None

    @classmethod
    def _extract_percentage(cls, text: str, labels: List[str]) -> Optional[int]:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        for line in lines:
            ll = line.lower()
            if labels and not any(label.lower() in ll for label in labels):
                continue
            m = re.search(r"(\d{1,2}(?:[.,]\d{1,2})?)\s*%", line)
            if not m:
                continue
            value = cls._norm_amount(m.group(1))
            if value is not None:
                return int(round(value))
        return None

    @classmethod
    def _extract_date_with_label(cls, text: str, labels: List[str]) -> Optional[str]:
        lower = (text or "").lower()
        for label in labels:
            idx = lower.find(label.lower())
            if idx == -1:
                continue
            window = text[idx: idx + 140]
            m = cls.DATE_RE.search(window)
            if not m:
                continue
            normalized = cls._norm_date(m.group(1))
            if normalized:
                return normalized
        m = cls.DATE_RE.search(text or "")
        return cls._norm_date(m.group(1)) if m else None

    @classmethod
    def _slice_from_keywords(cls, text: str, keywords: List[str]) -> str:
        lower = (text or "").lower()
        positions = [lower.find(k.lower()) for k in keywords if lower.find(k.lower()) != -1]
        if not positions:
            return text or ""
        start = min(positions)
        return (text or "")[start:]

    @staticmethod
    def _extract_regex(text: str, patterns: List[str], return_match: bool = False):
        for pattern in patterns:
            m = re.search(pattern, text or "", re.IGNORECASE)
            if m:
                if return_match:
                    return m
                return m.group(1).strip()
        return None

    @staticmethod
    def _line_looks_like_non_summary(lower_line: str) -> bool:
        blockers = [
            "litros",
            " litro",
            "l ",
            "precio unidad",
            "producto",
            "promo",
            "promocion",
            "descuento",
            "codigo",
            "barra",
            "matricula",
            "telefono",
            "articulo",
        ]
        return any(token in lower_line for token in blockers)

    @staticmethod
    def _is_unit_price_context(prefix: str, suffix: str) -> bool:
        context = f"{prefix} {suffix}"
        return any(token in context for token in ["/l", "l ", "litro", "precio", "unidad"])

    @staticmethod
    def _looks_like_rate(value: str) -> bool:
        return "%" in value or value.strip() in {"4", "10", "21", "4.00", "10.00", "21.00", "4,00", "10,00", "21,00"}

    @staticmethod
    def _norm_amount(raw: str) -> Optional[float]:
        if raw is None:
            return None
        value = raw.replace("€", "").replace(" ", "").replace("%", "")
        if not value:
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
            return round(float(Decimal(normalized)), 2)
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _norm_date(raw: str) -> Optional[str]:
        if not raw:
            return None
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(raw.strip(), fmt).date().isoformat()
            except ValueError:
                continue
        return None

    @staticmethod
    def _calc_rate(base: Optional[float], vat_amount: Optional[float]) -> Optional[int]:
        if not base or not vat_amount:
            return None
        if base == 0:
            return None
        value = round((vat_amount / base) * 100)
        if value in {4, 10, 21}:
            return int(value)
        return None

    @classmethod
    def _finalize(cls, data: Dict[str, Any]) -> None:
        for key in ["tax_base", "vat_amount", "total_amount"]:
            if data.get(key) is not None:
                data[key] = round(float(data[key]), 2)

        if data.get("tax_base") and data.get("vat_amount") and data.get("total_amount"):
            expected = round(data["tax_base"] + data["vat_amount"], 2)
            if abs(expected - data["total_amount"]) > 0.02:
                data["warnings"].append("Base + IVA no coincide con total")

        required = ["supplier_name", "invoice_number", "invoice_date", "tax_base", "vat_rate", "vat_amount", "total_amount"]
        data["needs_review"] = any(data.get(field) in (None, "") for field in required)

        score_fields = [
            "supplier_name",
            "supplier_tax_id",
            "invoice_number",
            "invoice_date",
            "tax_base",
            "vat_rate",
            "vat_amount",
            "total_amount",
        ]
        hits = sum(1 for f in score_fields if data.get(f) not in (None, ""))
        data["confidence"] = round(hits / len(score_fields), 2)

    @classmethod
    def _add_compat_aliases(cls, data: Dict[str, Any]) -> None:
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

    @classmethod
    def _log_parser_result(cls, parser_name: str, data: Dict[str, Any]) -> None:
        logger.info(
            "invoice_parser_v2 parser=%s invoice_number=%s invoice_date=%s tax_base=%s vat_rate=%s vat_amount=%s total_amount=%s warnings=%s",
            parser_name,
            data.get("invoice_number"),
            data.get("invoice_date"),
            data.get("tax_base"),
            data.get("vat_rate"),
            data.get("vat_amount"),
            data.get("total_amount"),
            data.get("warnings"),
        )

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
        }


InvoiceParser = InvoiceParserV2

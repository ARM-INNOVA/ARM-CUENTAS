import PyPDF2
from pdfplumber import PDF
import json
from typing import Optional, Dict, Any
import re
from decimal import Decimal

class InvoiceExtractor:
    """Extractor de datos de facturas"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extraer texto de PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extrayendo PDF: {e}")
        return text
    
    @staticmethod
    def extract_invoice_data(text: str) -> Dict[str, Any]:
        """Extraer datos de factura del texto"""
        data = {
            "fecha": None,
            "numero_factura": None,
            "proveedor": None,
            "nif_cif": None,
            "base_imponible": None,
            "iva_porcentaje": None,
            "iva_cantidad": None,
            "importe_total": None,
            "concepto": None,
            "confianza": 0
        }
        
        if not text:
            return data
        
        # Buscar fecha (formatos: DD/MM/YYYY, DD-MM-YYYY, etc.)
        fecha_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})', text)
        if fecha_match:
            data["fecha"] = fecha_match.group(1)
        
        # Buscar número de factura
        factura_match = re.search(r'(?:factura|F|Nº|N°|#)[\s:]*([A-Z0-9/\-\.]+)', text, re.IGNORECASE)
        if factura_match:
            data["numero_factura"] = factura_match.group(1).strip()
        
        # Buscar NIF/CIF
        nif_match = re.search(r'([A-Z0-9]{8,12}[-]?[0-9A-Z])', text)
        if nif_match:
            data["nif_cif"] = nif_match.group(1).strip()
        
        # Buscar importes (IVA, Base, Total)
        amounts = re.findall(r'(\d+[.,]\d{2})\s*€?', text)
        if amounts:
            amounts = [Decimal(a.replace('.', '').replace(',', '.')) for a in amounts]
            if len(amounts) >= 1:
                data["importe_total"] = float(amounts[-1])
            if len(amounts) >= 2:
                data["iva_cantidad"] = float(amounts[-2])
            if len(amounts) >= 3:
                data["base_imponible"] = float(amounts[-3])
        
        # Buscar porcentaje de IVA
        iva_match = re.search(r'(\d{1,2})\s*%\s*(?:IVA|iva)', text)
        if iva_match:
            data["iva_porcentaje"] = int(iva_match.group(1))
        else:
            # Detectar por defecto si no aparece
            if data["iva_cantidad"] and data["base_imponible"]:
                calculated_pct = int((float(data["iva_cantidad"]) / float(data["base_imponible"])) * 100)
                if calculated_pct in [4, 10, 21]:
                    data["iva_porcentaje"] = calculated_pct
        
        # Detectar confianza
        confidence = 0
        if data["numero_factura"]:
            confidence += 20
        if data["fecha"]:
            confidence += 20
        if data["importe_total"]:
            confidence += 20
        if data["nif_cif"]:
            confidence += 20
        if data["iva_cantidad"] and data["base_imponible"]:
            confidence += 20
        
        data["confianza"] = min(confidence, 100)
        
        return data
    
    @staticmethod
    def detect_invoice_type(text: str) -> str:
        """Detectar si es ingreso o gasto"""
        text_lower = text.lower()
        
        # Palabras clave para ingresos
        ingreso_keywords = ["factura de venta", "invoice", "factura emitida", "venta", "ingresos"]
        for keyword in ingreso_keywords:
            if keyword in text_lower:
                return "ingreso"
        
        # Palabras clave para gastos
        gasto_keywords = ["factura de compra", "purchase", "factura recibida", "gasto", "compra"]
        for keyword in gasto_keywords:
            if keyword in text_lower:
                return "gasto"
        
        return "gasto"  # Por defecto, considerar gasto

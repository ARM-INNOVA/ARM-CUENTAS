import unittest

from app.services.invoice_parser_v2 import InvoiceParserV2


class InvoiceParserV2Tests(unittest.TestCase):
    def test_ballenoil_parser_exact_values(self):
        text = """
        BALLENOIL, S.A.
        1491848 31/05/2026 FRA/1000022383
        09/05/2026 Gasoil Excellent 57.18L 1.639€ 93.72€
        03/05/2026 Diesel 52.15L 1.629€ 84.95€
        162.43€
        10% 16.24€
        178.67€
        PAGADO
        Adjuntamos en la última hoja
        """
        data = InvoiceParserV2.parse_text(text)

        self.assertEqual(data["supplier_name"], "BALLENOIL, S.A.")
        self.assertEqual(data["supplier_tax_id"], "A65371171")
        self.assertEqual(data["invoice_number"], "FRA/1000022383")
        self.assertEqual(data["invoice_date"], "2026-05-31")
        self.assertEqual(data["operation_date"], "2026-05-09")
        self.assertEqual(data["tax_base"], 162.43)
        self.assertEqual(data["vat_rate"], 10)
        self.assertEqual(data["vat_amount"], 16.24)
        self.assertEqual(data["total_amount"], 178.67)
        self.assertEqual(data["payment_status"], "pagado")
        self.assertIsNone(data["payment_method"])
        self.assertFalse(data["needs_review"])

        self.assertNotEqual(data["total_amount"], 57.18)
        self.assertNotEqual(data["total_amount"], 52.15)
        self.assertNotEqual(data["total_amount"], 93.72)
        self.assertNotEqual(data["total_amount"], 84.95)
        self.assertIsNotNone(data["tax_base"])
        self.assertIsNotNone(data["vat_amount"])
        self.assertIsNotNone(data["total_amount"])
        self.assertIsNotNone(data["supplier_tax_id"])

    def test_ballenoil_does_not_use_liters_as_amounts(self):
        text = """
        BALLENOIL, S.A.
        Número factura: FRA/1000022383
        Fecha factura: 31/05/2026
        Línea combustible 1: 57.18L 1.639€ 93.72€
        Línea combustible 2: 52.15L 1.629€ 84.95€
        Base imponible: 162.43€
        IVA: 10% 16.24€
        Total factura: 178.67€
        """
        data = InvoiceParserV2.parse_text(text)

        self.assertEqual(data["supplier_name"], "BALLENOIL, S.A.")
        self.assertEqual(data["invoice_number"], "FRA/1000022383")
        self.assertEqual(data["invoice_date"], "2026-05-31")
        self.assertEqual(data["tax_base"], 162.43)
        self.assertEqual(data["vat_rate"], 10)
        self.assertEqual(data["vat_amount"], 16.24)
        self.assertEqual(data["total_amount"], 178.67)

        self.assertNotEqual(data["total_amount"], 57.18)
        self.assertNotEqual(data["total_amount"], 52.15)
        self.assertNotEqual(data["total_amount"], 93.72)
        self.assertNotEqual(data["total_amount"], 84.95)

    def test_bricodepot_uses_tax_summary(self):
        text = """
        Euro Depot España S.A.U.
        bricodepot.es
        Nº factura: FT 2026163803/00007486
        Fecha: 26/05/2026
        PUNTAL PROFESIONAL ... Total linea IVA: 54.22
        Total EUR 54.22
        Base 44.81
        EFECTIVO 54.22 9.41
        Base Cuota Recargo Total
        44.81 € 21% 9.41 € 0,00% 0.00€ 54.22 €
        Total 44.81 € 9.41 € 0.00 € 54.22 €
        """
        data = InvoiceParserV2.parse_text(text)

        self.assertEqual(data["supplier_name"], "Euro Depot España S.A.U.")
        self.assertEqual(data["supplier_tax_id"], "A62018064")
        self.assertEqual(data["invoice_number"], "FT 2026163803/00007486")
        self.assertEqual(data["invoice_date"], "2026-05-26")
        self.assertEqual(data["tax_base"], 44.81)
        self.assertEqual(data["vat_rate"], 21)
        self.assertEqual(data["vat_amount"], 9.41)
        self.assertEqual(data["total_amount"], 54.22)

    def test_leroy_merlin_total_uses_tti_not_si(self):
        text = """
        Leroy Merlin España S.L.U.
        FACTURA 052-0007-270411
        Fecha de venta: 02/04/2026
        Gijon, a 7 Julio 2026
        Total SI (EUR): 1,37
        Tasa IVA: 21,00
        Precio Unidad TTI: 1,66
        Importe TTI: 1,66
        Tasa IVA/IGIC/IPSI Total SI (EUR) Total IVA/IGIC/IPSI Total TII (EUR)
        21.00 1,37 0,29 1,66
        EUR 1,37 0,29 1,66
        """
        data = InvoiceParserV2.parse_text(text)

        self.assertEqual(data["supplier_name"], "Leroy Merlin España S.L.U.")
        self.assertEqual(data["supplier_tax_id"], "B84818442")
        self.assertEqual(data["invoice_number"], "052-0007-270411")
        self.assertEqual(data["invoice_date"], "2026-04-02")
        self.assertEqual(data["tax_base"], 1.37)
        self.assertEqual(data["vat_rate"], 21)
        self.assertEqual(data["vat_amount"], 0.29)
        self.assertEqual(data["total_amount"], 1.66)
        self.assertNotEqual(data["total_amount"], 1.37)


if __name__ == "__main__":
    unittest.main()

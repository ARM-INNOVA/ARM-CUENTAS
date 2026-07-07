import unittest

from app.services.invoice_parser import InvoiceParser


class InvoiceParserProviderTests(unittest.TestCase):
    def test_saltoki_29471(self):
        text = """
        SALTOKI ASTURIAS, S.L.
        CIF B74377516
        CLIENTE / FECHA / NÚMERO 25/05/2026 29471
        BASE IMPONIBLE   % I.V.A.   I.V.A.   TOTAL
        15,50            21         3,26     18,76
        """
        data = InvoiceParser.parse_text(text)
        self.assertEqual(data["invoice_date"], "2026-05-25")
        self.assertEqual(data["invoice_number"], "29471")
        self.assertAlmostEqual(data["tax_base"], 15.50, places=2)
        self.assertAlmostEqual(data["vat_amount"], 3.26, places=2)
        self.assertAlmostEqual(data["total_amount"], 18.76, places=2)

    def test_saltoki_29617(self):
        text = """
        SALTOKI ASTURIAS, S.L.
        CIF B74377516
        CLIENTE / FECHA / NÚMERO 27/05/2026 29617
        BASE IMPONIBLE   % I.V.A.   I.V.A.   TOTAL
        8,88             21         1,86     10,74
        """
        data = InvoiceParser.parse_text(text)
        self.assertEqual(data["invoice_date"], "2026-05-27")
        self.assertEqual(data["invoice_number"], "29617")
        self.assertAlmostEqual(data["tax_base"], 8.88, places=2)
        self.assertAlmostEqual(data["vat_amount"], 1.86, places=2)
        self.assertAlmostEqual(data["total_amount"], 10.74, places=2)

    def test_ballenoil(self):
        text = """
        BALLENOIL, S.A.
        FRA/1000022383
        Fecha factura: 31/05/2026
        Base imponible 162,43
        IVA 10% 16,24
        Total factura 178,67
        """
        data = InvoiceParser.parse_text(text)
        self.assertEqual(data["invoice_number"], "FRA/1000022383")
        self.assertEqual(data["invoice_date"], "2026-05-31")
        self.assertEqual(data["vat_rate"], 10)
        self.assertAlmostEqual(data["tax_base"], 162.43, places=2)
        self.assertAlmostEqual(data["vat_amount"], 16.24, places=2)
        self.assertAlmostEqual(data["total_amount"], 178.67, places=2)

    def test_obramat(self):
        text = """
        BRICOLAJE BRICOMAN, S.L.U. OBRAMAT
        Factura 002-0005-548466
        Fecha 29/05/2026
        Tasa IVA/IGIC/IPSI   Total SI   Total IVA   Total TTI
        21%                  241,14     50,64       291,78
        Efectivo 300,00
        Cambio 8,22
        """
        data = InvoiceParser.parse_text(text)
        self.assertEqual(data["invoice_number"], "002-0005-548466")
        self.assertEqual(data["invoice_date"], "2026-05-29")
        self.assertAlmostEqual(data["tax_base"], 241.14, places=2)
        self.assertAlmostEqual(data["vat_amount"], 50.64, places=2)
        self.assertAlmostEqual(data["total_amount"], 291.78, places=2)

    def test_obramat_total_uses_summary_not_first_line(self):
        text = """
        BRICOLAJE BRICOMAN, S.L.U. OBRAMAT
        Factura 002-0005-548466
        Producto A 1 2,70 2,70
        Producto B 1 119,00 119,00
        Producto C 1 155,00 155,00
        Producto D 1 15,08 15,08
        Tasa IVA/IGIC/IPSI   Total. SI (EUR)   Total IVA/IGIC/IPSI   Total TTI (EUR)
        21.00               241.14            50.64                  291,78
        EFECTIVO 300,00
        CAMBIO 8,22
        """
        data = InvoiceParser.parse_text(text)
        self.assertAlmostEqual(data["total_amount"], 291.78, places=2)
        self.assertAlmostEqual(data["tax_base"], 241.14, places=2)
        self.assertAlmostEqual(data["vat_amount"], 50.64, places=2)

        self.assertNotEqual(data["total_amount"], 2.70)
        self.assertNotEqual(data["total_amount"], 119.00)
        self.assertNotEqual(data["total_amount"], 155.00)
        self.assertNotEqual(data["total_amount"], 15.08)
        self.assertNotEqual(data["total_amount"], 300.00)
        self.assertNotEqual(data["total_amount"], 8.22)

    def test_brico_depot(self):
        text = """
        Euro Depot España S.A.U. Brico Depot
        Nº factura FT 2026163803/00007483
        Fecha factura 26/05/2026
        Base   Cuota   Recargo   Total
        90,08  18,92   0,00      109,00
        """
        data = InvoiceParser.parse_text(text)
        self.assertEqual(data["invoice_number"], "FT 2026163803/00007483")
        self.assertEqual(data["invoice_date"], "2026-05-26")
        self.assertAlmostEqual(data["tax_base"], 90.08, places=2)
        self.assertAlmostEqual(data["vat_amount"], 18.92, places=2)
        self.assertAlmostEqual(data["total_amount"], 109.00, places=2)

    def test_leroy_merlin(self):
        text = """
        Leroy Merlin España S.L.U.
        Factura 052-0007-270411
        Fecha de venta: 02/04/2026
        Fecha de emisión: 7 Julio 2026
        Base imponible 1,37
        IVA 21% 0,29
        Total factura 1,66
        """
        data = InvoiceParser.parse_text(text)
        self.assertEqual(data["invoice_number"], "052-0007-270411")
        self.assertEqual(data["sale_date"], "2026-04-02")
        self.assertEqual(data["invoice_date"], "2026-04-02")
        self.assertAlmostEqual(data["tax_base"], 1.37, places=2)
        self.assertAlmostEqual(data["vat_amount"], 0.29, places=2)
        self.assertAlmostEqual(data["total_amount"], 1.66, places=2)


if __name__ == "__main__":
    unittest.main()

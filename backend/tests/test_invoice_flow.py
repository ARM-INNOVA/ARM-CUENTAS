import io
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import fitz
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.middleware.auth import get_current_user
from app.models.file import File as FileModel
from app.models.user import User, UserRole
from app.routes import files, movements
from app.config import settings


class InvoiceFlowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        self.tmp_upload_dir = tempfile.mkdtemp(prefix="arm_uploads_")
        self.previous_upload_dir = settings.UPLOAD_DIR
        settings.UPLOAD_DIR = self.tmp_upload_dir

        db = self.SessionLocal()
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="x",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        self.user_id = user.id
        db.close()

        app = FastAPI()
        app.include_router(files.router)
        app.include_router(movements.router)

        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        def override_current_user():
            db = self.SessionLocal()
            try:
                return db.query(User).filter(User.id == self.user_id).first()
            finally:
                db.close()

        from app.database import get_db

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_current_user

        self.client = TestClient(app)

    def tearDown(self):
        settings.UPLOAD_DIR = self.previous_upload_dir
        Base.metadata.drop_all(bind=self.engine)

    @staticmethod
    def _build_ballenoil_pdf_bytes() -> bytes:
        text = """
BALLENOIL, S.A.
1491848 31/05/2026 FRA/1000022383
09/05/2026 Gasoil Excellent 57.18L 1.639€ 93.72€
03/05/2026 Diesel 52.15L 1.629€ 84.95€
162.43€
10% 16.24€
178.67€
PAGADO
""".strip()
        doc = fitz.open()
        page = doc.new_page()
        page.insert_textbox((36, 36, 560, 800), text, fontsize=11)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def _upload_ballenoil_invoice(self):
        pdf_bytes = self._build_ballenoil_pdf_bytes()
        files_payload = {
            "file": ("ballenoil.pdf", io.BytesIO(pdf_bytes), "application/pdf")
        }
        return self.client.post("/api/files/upload", files=files_payload)

    def _confirm_payload(self):
        return {
            "fecha": datetime(2026, 5, 9, 9, 0).isoformat(),
            "tipo": "gasto",
            "concepto": "BALLENOIL, S.A.",
            "descripcion": "Factura Ballenoil",
            "obra_id": None,
            "categoria_id": None,
            "proveedor_id": None,
            "numero_factura": "FRA/1000022383",
            "nif_cif": "A65371171",
            "base_imponible": 162.43,
            "iva_porcentaje": 10,
            "iva_cantidad": 16.24,
            "importe_total": 178.67,
            "forma_pago": "transferencia",
            "estado": "pendiente",
            "observaciones": "",
            "needs_review": False,
        }

    def test_upload_invoice_creates_pending_invoice_record(self):
        response = self._upload_ballenoil_invoice()
        self.assertEqual(response.status_code, 201, response.text)

        payload = response.json()
        self.assertIn("file_id", payload)
        self.assertTrue((payload.get("texto_extraido") or "").strip())

        db = self.SessionLocal()
        try:
            file_row = db.query(FileModel).filter(FileModel.id == payload["file_id"]).first()
            self.assertIsNotNone(file_row)
            self.assertIsNone(file_row.movement_id)
            self.assertIsNotNone(file_row.datos_extraidos)
        finally:
            db.close()

    def test_confirm_invoice_creates_movement(self):
        upload = self._upload_ballenoil_invoice()
        self.assertEqual(upload.status_code, 201, upload.text)
        file_id = upload.json()["file_id"]

        confirm = self.client.post(f"/api/files/{file_id}/review", json=self._confirm_payload())
        self.assertEqual(confirm.status_code, 201, confirm.text)
        body = confirm.json()

        self.assertIn("movement_id", body)
        self.assertEqual(body["file_id"], file_id)

        db = self.SessionLocal()
        try:
            file_row = db.query(FileModel).filter(FileModel.id == file_id).first()
            self.assertIsNotNone(file_row.movement_id)
            self.assertFalse(file_row.necesita_revision)
        finally:
            db.close()

    def test_movements_list_returns_created_movement(self):
        upload = self._upload_ballenoil_invoice()
        self.assertEqual(upload.status_code, 201, upload.text)
        file_id = upload.json()["file_id"]

        confirm = self.client.post(f"/api/files/{file_id}/review", json=self._confirm_payload())
        self.assertEqual(confirm.status_code, 201, confirm.text)
        movement_id = confirm.json()["movement_id"]

        listed = self.client.get("/api/movements/")
        self.assertEqual(listed.status_code, 200, listed.text)
        data = listed.json()
        created = next((item for item in data if item["id"] == movement_id), None)

        self.assertIsNotNone(created)
        self.assertEqual(created["numero_factura"], "FRA/1000022383")
        self.assertEqual(float(created["base_imponible"]), 162.43)
        self.assertEqual(created["iva_porcentaje"], 10)
        self.assertEqual(float(created["iva_cantidad"]), 16.24)
        self.assertEqual(float(created["importe_total"]), 178.67)


if __name__ == "__main__":
    unittest.main()

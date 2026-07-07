import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.provider import Provider
from app.services.provider_service import ProviderService


class ProviderServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=self.engine)

    def test_get_providers_activos_only(self):
        db = self.SessionLocal()
        try:
            db.add(Provider(nombre="Activo", tipo="proveedor", activo=True))
            db.add(Provider(nombre="Inactivo", tipo="proveedor", activo=False))
            db.commit()

            providers = ProviderService.get_providers(db, activos_only=True)
            names = [p.nombre for p in providers]

            self.assertIn("Activo", names)
            self.assertNotIn("Inactivo", names)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()

import os
from pathlib import Path

TEST_DB_PATH = Path(__file__).resolve().parent / "test_travel_agency.db"
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["TRAVEL_AGENCY_DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

import pytest
from fastapi.testclient import TestClient

from server.database import Base, engine, SessionLocal
from server.main import app, create_default_admin, create_demo_data


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    create_default_admin()
    create_demo_data()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def api_client():
    return TestClient(app)


@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

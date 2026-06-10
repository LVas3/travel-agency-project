import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.main import app
from server.database import Base, get_db


TEST_DB_FILE = "test_travel_agency.db"
TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_FILE}"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()

        Base.metadata.drop_all(bind=engine)

        # Важно для Windows: полностью закрываем соединения с SQLite.
        # Файл test_travel_agency.db не удаляем вручную, потому что на Windows
        # SQLite иногда ещё держит его занятым. Таблицы перед каждым тестом
        # всё равно пересоздаются через drop_all/create_all.
        engine.dispose()


@pytest.fixture(scope="function")
def api_client(db_session):
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
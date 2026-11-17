import os
import tempfile

os.environ["DATABASE_PATH"] = os.path.join(
    tempfile.mkdtemp(prefix="book-api-test-"), "test.db"
)

import pytest
from fastapi.testclient import TestClient

from app.main import DB_PATH, app, init_db


@pytest.fixture(autouse=True)
def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

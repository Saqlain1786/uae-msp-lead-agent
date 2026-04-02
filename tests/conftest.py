from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database import init_db
from app.main import app


@pytest.fixture
def client(tmp_path: Path):
    settings.database_path = str(tmp_path / "test.db")
    init_db()
    with TestClient(app) as c:
        yield c

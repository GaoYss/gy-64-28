import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.data.store import InMemoryStore, store


@pytest.fixture
def fresh_store():
    original_store = store
    new_store = InMemoryStore()
    import app.data.store as data_module
    data_module.store = new_store
    yield new_store
    data_module.store = original_store


@pytest.fixture
def client(fresh_store):
    with TestClient(app) as c:
        yield c

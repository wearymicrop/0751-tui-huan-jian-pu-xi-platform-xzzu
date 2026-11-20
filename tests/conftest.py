import pytest
from fastapi.testclient import TestClient
from app.analysis import analyze
from app.main import app
from app.source import load_sample


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LINEAGE_DB", str(tmp_path / "archive.sqlite3"))
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def clean():
    return load_sample("clean")


@pytest.fixture
def dirty():
    return load_sample("dirty")


@pytest.fixture
def dirty_report(dirty):
    return analyze(dirty)


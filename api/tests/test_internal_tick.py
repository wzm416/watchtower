"""Internal cron route tests — requires Postgres for DB session."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from watchtower_api.db.session import get_db, get_engine
from watchtower_api.main import app

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set",
)


@pytest.fixture
def db_session() -> Session:
    engine = get_engine()
    maker = sessionmaker(bind=engine)
    db = maker()
    db.execute(text("TRUNCATE users CASCADE"))
    db.commit()
    try:
        yield db
    finally:
        db.close()


def test_tick_requires_bearer(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> None:
    monkeypatch.setenv("CRON_BEARER_TOKEN", "cron-test-secret")

    def override_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        c = TestClient(app)
        assert c.post("/internal/jobs/tick").status_code == 401
        r = c.post(
            "/internal/jobs/tick",
            headers={"Authorization": "Bearer wrong"},
        )
        assert r.status_code == 401
        ok = c.post(
            "/internal/jobs/tick",
            headers={"Authorization": "Bearer cron-test-secret"},
        )
        assert ok.status_code == 200
        data = ok.json()
        assert data["due_candidates"] == 0
        assert data["processed"] == 0
        assert data["errors"] == []
    finally:
        app.dependency_overrides.clear()


def test_tick_not_configured(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> None:
    monkeypatch.delenv("CRON_BEARER_TOKEN", raising=False)

    def override_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        c = TestClient(app)
        r = c.post(
            "/internal/jobs/tick",
            headers={"Authorization": "Bearer anything"},
        )
        assert r.status_code == 503
    finally:
        app.dependency_overrides.clear()

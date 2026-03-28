"""API tests for monitors — requires Postgres; auth overridden to a fixed user."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from watchtower_api.db.session import get_db, get_engine
from watchtower_api.deps import get_current_user
from watchtower_api.main import app
from watchtower_api.models import Monitor, User

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


@pytest.fixture
def api_client(db_session: Session) -> TestClient:
    user = User(google_sub="api-test-user", email="api@test.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    def override_db() -> Session:
        yield db_session

    def override_user() -> User:
        return user

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_list_empty(api_client: TestClient) -> None:
    r = api_client.get("/api/v1/monitors")
    assert r.status_code == 200
    assert r.json() == []


def test_create_get_patch_delete(api_client: TestClient) -> None:
    body = {
        "label": "Shoes",
        "product_url": "https://example.com/p/1",
        "schedule_cron": "0 * * * *",
        "timezone": "America/Los_Angeles",
    }
    r = api_client.post("/api/v1/monitors", json=body)
    assert r.status_code == 201
    created = r.json()
    mid = created["id"]
    assert created["label"] == "Shoes"
    assert created["product_url"] == "https://example.com/p/1"

    r = api_client.get(f"/api/v1/monitors/{mid}")
    assert r.status_code == 200
    assert r.json()["id"] == mid

    r = api_client.patch(f"/api/v1/monitors/{mid}", json={"label": "Boots"})
    assert r.status_code == 200
    assert r.json()["label"] == "Boots"

    r = api_client.delete(f"/api/v1/monitors/{mid}")
    assert r.status_code == 204

    r = api_client.get(f"/api/v1/monitors/{mid}")
    assert r.status_code == 404


def test_reject_non_https_product_url(api_client: TestClient) -> None:
    r = api_client.post(
        "/api/v1/monitors",
        json={
            "product_url": "http://insecure.example.com/x",
            "schedule_cron": "0 * * * *",
        },
    )
    assert r.status_code == 422


def test_other_user_404(api_client: TestClient, db_session: Session) -> None:
    owner = User(google_sub="owner-1", email="owner@test.com")
    other = User(google_sub="other-1", email="other@test.com")
    db_session.add_all([owner, other])
    db_session.commit()
    db_session.refresh(owner)
    mon = Monitor(
        user_id=owner.id,
        product_url="https://example.com/secret",
        schedule_cron="0 * * * *",
    )
    db_session.add(mon)
    db_session.commit()
    db_session.refresh(mon)

    def override_db() -> Session:
        yield db_session

    def override_user() -> User:
        return other

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    try:
        c = TestClient(app)
        r = c.get(f"/api/v1/monitors/{mon.id}")
        assert r.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_random_uuid_404(api_client: TestClient) -> None:
    r = api_client.get(f"/api/v1/monitors/{uuid.uuid4()}")
    assert r.status_code == 404


def test_google_auth_not_configured(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> None:
    monkeypatch.delenv("GOOGLE_CLIENT_IDS", raising=False)

    def override_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_user, None)
    try:
        c = TestClient(app)
        r = c.get("/api/v1/monitors", headers={"Authorization": "Bearer x"})
        assert r.status_code == 503
    finally:
        app.dependency_overrides.clear()

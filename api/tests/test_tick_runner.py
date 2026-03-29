"""Tick runner integration — requires Postgres."""

from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from watchtower_api.config import get_settings
from watchtower_api.db.session import get_engine
from watchtower_api.models import Monitor, User
from watchtower_api.models.monitor import MonitorStatus
from watchtower_api.services import fetch_product
from watchtower_api.services.tick_runner import process_tick

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


def test_process_tick_parses_price(monkeypatch: pytest.MonkeyPatch, db_session: Session) -> None:
    monkeypatch.delenv("RESEND_API_KEY", raising=False)

    def fake_fetch(url: str, *, timeout_seconds: float = 10.0) -> tuple[int, str]:
        return 200, "<html><body><span class='p'>$9.99</span></body></html>"

    monkeypatch.setattr(fetch_product, "fetch_html", fake_fetch)

    user = User(google_sub="tick-u1", email="t@example.com")
    db_session.add(user)
    db_session.flush()
    mon = Monitor(
        user_id=user.id,
        product_url="https://example.com/product",
        schedule_cron="0 * * * *",
        timezone="UTC",
        status=MonitorStatus.ACTIVE.value,
        css_selector=".p",
        next_run_at=datetime(2020, 1, 1, tzinfo=UTC),
    )
    db_session.add(mon)
    db_session.commit()

    out = process_tick(db_session, get_settings(), limit=5)
    assert out["processed"] == 1
    assert out["due_candidates"] == 1
    db_session.refresh(mon)
    assert mon.last_price_minor == 999
    assert mon.last_currency == "USD"

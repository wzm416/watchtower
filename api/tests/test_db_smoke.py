"""Integration tests against Postgres — skipped when DATABASE_URL is unset."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from watchtower_api.db.session import get_engine
from watchtower_api.models import Monitor, PriceSnapshot, Run, User

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set (local Postgres or CI service required)",
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


def test_roundtrip_user_monitor(db_session: Session) -> None:
    user = User(google_sub="gid-test-1", email="u@example.com")
    db_session.add(user)
    db_session.flush()
    mon = Monitor(
        user_id=user.id,
        product_url="https://example.com/item",
        schedule_cron="*/5 * * * *",
        label="Widget",
    )
    db_session.add(mon)
    db_session.commit()

    loaded = db_session.execute(select(Monitor).where(Monitor.id == mon.id)).scalar_one()
    assert loaded.label == "Widget"
    assert loaded.user_id == user.id


def test_price_snapshot_one_per_run(db_session: Session) -> None:
    user = User(google_sub="gid-test-2", email="x@example.com")
    db_session.add(user)
    db_session.flush()
    mon = Monitor(
        user_id=user.id,
        product_url="https://example.com/p",
        schedule_cron="0 * * * *",
    )
    db_session.add(mon)
    db_session.flush()
    run = Run(monitor_id=mon.id)
    db_session.add(run)
    db_session.flush()
    db_session.add(
        PriceSnapshot(
            monitor_id=mon.id,
            run_id=run.id,
            amount_minor=12_99,
            currency="USD",
            confidence=0.99,
        )
    )
    db_session.commit()

    dup = PriceSnapshot(
        monitor_id=mon.id,
        run_id=run.id,
        amount_minor=11_99,
        currency="USD",
        confidence=0.5,
    )
    db_session.add(dup)
    with pytest.raises(IntegrityError):
        db_session.commit()

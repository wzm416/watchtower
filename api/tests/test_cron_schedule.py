from __future__ import annotations

from datetime import UTC, datetime

import pytest
from watchtower_api.services.cron_schedule import next_run_utc


def test_next_run_hourly_utc() -> None:
    start = datetime(2026, 3, 28, 12, 30, tzinfo=UTC)
    nxt = next_run_utc("0 * * * *", "UTC", start)
    assert nxt == datetime(2026, 3, 28, 13, 0, tzinfo=UTC)


def test_invalid_cron() -> None:
    with pytest.raises(ValueError, match="Invalid cron"):
        next_run_utc("not a cron", "UTC")


def test_invalid_timezone() -> None:
    with pytest.raises(ValueError, match="Unknown timezone"):
        next_run_utc("0 * * * *", "Nowhere/Invalid")

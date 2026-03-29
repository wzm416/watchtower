from __future__ import annotations

from watchtower_api.services.schedule_nl import natural_language_to_cron


def test_every_hour() -> None:
    assert natural_language_to_cron("every hour") == "0 * * * *"


def test_raw_cron_pass_through() -> None:
    assert natural_language_to_cron("15 10 * * *") == "15 10 * * *"


def test_unknown() -> None:
    assert natural_language_to_cron("whenever I feel like it") is None

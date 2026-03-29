from __future__ import annotations

from watchtower_api.services.money_parse import parse_price


def test_usd() -> None:
    r = parse_price("Sale price $19.99 today")
    assert r is not None
    minor, cur, conf = r
    assert cur == "USD"
    assert minor == 1999


def test_eur_suffix() -> None:
    r = parse_price("12,99 €")
    assert r is not None
    assert r[1] == "EUR"


def test_gbp() -> None:
    r = parse_price("£1,234.50")
    assert r is not None
    assert r[0] == 123_450
    assert r[1] == "GBP"

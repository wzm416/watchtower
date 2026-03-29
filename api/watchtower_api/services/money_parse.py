"""Parse price strings from scraped text into minor units + ISO currency."""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def parse_price(text: str) -> tuple[int, str, float] | None:
    """
    Return (amount_minor, currency_iso, confidence) or None.
    Confidence is heuristic 0–1 based on pattern clarity.
    """
    raw = re.sub(r"\s+", " ", text.strip())
    if not raw:
        return None

    # USD $12.99 or $1,234.56
    if m := re.search(r"\$\s*([\d,]+(?:\.\d{1,2})?)", raw):
        return _decimal_to_minor(m.group(1), "USD", 0.9)

    # EUR 12,99 or 12.99 €
    if m := re.search(r"([\d.,]+)\s*€", raw):
        return _parse_eu_style(m.group(1), "EUR", 0.85)
    if m := re.search(r"€\s*([\d.,]+)", raw):
        return _parse_eu_style(m.group(1), "EUR", 0.85)

    # GBP £12.99
    if m := re.search(r"£\s*([\d,]+(?:\.\d{1,2})?)", raw):
        return _decimal_to_minor(m.group(1), "GBP", 0.9)

    # USD without symbol: trailing USD
    if m := re.search(r"([\d,]+(?:\.\d{1,2})?)\s*USD\b", raw, re.I):
        return _decimal_to_minor(m.group(1), "USD", 0.65)

    return None


def _parse_eu_style(num: str, currency: str, conf: float) -> tuple[int, str, float] | None:
    s = num.strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s and "." not in s:
        if re.fullmatch(r"\d+,\d{2}", s):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    return _decimal_to_minor(s, currency, conf)


def _decimal_to_minor(num: str, currency: str, conf: float) -> tuple[int, str, float] | None:
    try:
        d = Decimal(num.replace(",", ""))
    except (InvalidOperation, ValueError):
        return None
    minor = int((d * 100).to_integral_value(rounding=ROUND_HALF_UP))
    return minor, currency, conf

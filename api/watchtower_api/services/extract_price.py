"""Extract a price from HTML using a CSS selector or light heuristics."""

from __future__ import annotations

from bs4 import BeautifulSoup

from watchtower_api.services.money_parse import parse_price


def extract_from_html(
    html: str,
    css_selector: str | None,
) -> tuple[int, str, float, str] | None:
    """
    Return (amount_minor, currency, confidence, snippet) or None.
    """
    soup = BeautifulSoup(html, "lxml")

    if css_selector:
        node = soup.select_one(css_selector)
        if node is None:
            return None
        text = node.get_text(" ", strip=True)
        parsed = parse_price(text)
        if parsed is None:
            return None
        minor, cur, conf = parsed
        return minor, cur, min(0.99, conf + 0.05), text[:500]

    # Heuristic: first price-like token in visible text order
    for tag in soup.find_all(string=True):
        if not tag.parent or tag.parent.name in {"script", "style", "noscript"}:
            continue
        t = str(tag).strip()
        if len(t) > 200:
            continue
        parsed = parse_price(t)
        if parsed:
            minor, cur, conf = parsed
            return minor, cur, conf * 0.7, t[:500]

    return None

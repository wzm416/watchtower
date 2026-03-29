"""Best-effort natural-language → cron hints (no full NLP)."""

from __future__ import annotations

import re


def _looks_like_five_field_cron(parts: list[str]) -> bool:
    field = re.compile(r"^[\d*,/\-]+$")
    return len(parts) == 5 and all(field.fullmatch(p) for p in parts)


def natural_language_to_cron(text: str) -> str | None:
    """
    Map common English phrases to 5-field cron (minute hour dom month dow).
    Returns None if no pattern matches — caller should ask for explicit cron.
    """
    t = text.strip().lower()
    if not t:
        return None

    parts = t.split()
    if _looks_like_five_field_cron(parts):
        return " ".join(parts)

    if re.fullmatch(r"every\s+minute", t):
        return "* * * * *"
    if re.fullmatch(r"every\s+hour", t):
        return "0 * * * *"
    if m := re.fullmatch(r"every\s+day\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", t):
        hour, minute, ampm = int(m.group(1)), int(m.group(2) or "0"), m.group(3)
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        return f"{minute} {hour} * * *"
    if re.fullmatch(r"every\s+weekday", t) or re.fullmatch(r"weekdays?", t):
        return "0 9 * * 1-5"
    if re.fullmatch(r"every\s+week\s+on\s+sunday", t) or re.fullmatch(r"weekly\s+on\s+sunday", t):
        return "0 9 * * 0"
    if re.fullmatch(r"every\s+week\s+on\s+monday", t) or re.fullmatch(r"weekly\s+on\s+monday", t):
        return "0 9 * * 1"

    return None

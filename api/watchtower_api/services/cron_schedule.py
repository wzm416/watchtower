"""Compute next cron fire time in a user timezone (wall-clock cron)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from croniter import CroniterBadCronError, croniter


def next_run_utc(cron_expr: str, timezone_name: str, after_utc: datetime | None = None) -> datetime:
    """
    Return the next scheduled instant at or strictly after `after_utc` (default: now UTC),
    interpreting the 5-field cron in `timezone_name` wall time.
    """
    if after_utc is None:
        after_utc = datetime.now(UTC)
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as e:
        msg = f"Unknown timezone: {timezone_name}"
        raise ValueError(msg) from e

    local_after = after_utc.astimezone(tz)
    try:
        itr = croniter(cron_expr, local_after)
        nxt = itr.get_next(datetime)
    except CroniterBadCronError as e:
        msg = f"Invalid cron expression: {cron_expr!r}"
        raise ValueError(msg) from e

    if nxt.tzinfo is None:
        nxt = nxt.replace(tzinfo=tz)
    return nxt.astimezone(UTC)


def next_run_after_execution(cron_expr: str, timezone_name: str) -> datetime:
    """Next run strictly after 'now' (avoids re-selecting the same second)."""
    return next_run_utc(cron_expr, timezone_name, datetime.now(UTC) + timedelta(seconds=1))

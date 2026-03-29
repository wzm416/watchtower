"""Process due monitors: fetch, parse, snapshot, notify, advance schedule."""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from watchtower_api.config import Settings
from watchtower_api.models import Monitor, Notification, PriceSnapshot, Run
from watchtower_api.models.monitor import MonitorStatus
from watchtower_api.services import cron_schedule, extract_price, fetch_product
from watchtower_api.services.email_resend import send_email

logger = logging.getLogger(__name__)


def _notify_reason(
    prev_minor: int | None,
    new_minor: int,
    target_minor: int | None,
) -> str | None:
    if prev_minor is None:
        return "first_price"
    if new_minor < prev_minor:
        return "price_drop"
    if target_minor is not None and new_minor <= target_minor and prev_minor > target_minor:
        return "target_hit"
    return None


def _dedupe_key(monitor_id: str, day_iso: str, reason: str, new_minor: int) -> str:
    raw = f"{monitor_id}|{day_iso}|{reason}|{new_minor}"
    return hashlib.sha256(raw.encode()).hexdigest()


def refresh_monitor_next_run(mon: Monitor) -> None:
    if mon.status != MonitorStatus.ACTIVE.value:
        mon.next_run_at = None
        return
    try:
        mon.next_run_at = cron_schedule.next_run_after_execution(mon.schedule_cron, mon.timezone)
    except ValueError:
        logger.warning("Bad cron for monitor %s: %s", mon.id, mon.schedule_cron)
        mon.next_run_at = None


def process_tick(db: Session, settings: Settings, *, limit: int = 20) -> dict[str, Any]:
    now = datetime.now(UTC)
    stmt = (
        select(Monitor)
        .options(selectinload(Monitor.user))
        .where(
            Monitor.status == MonitorStatus.ACTIVE.value,
            or_(Monitor.next_run_at.is_(None), Monitor.next_run_at <= now),
        )
        .order_by(Monitor.next_run_at.asc().nulls_first())
        .limit(limit)
    )
    monitors = list(db.scalars(stmt).all())
    processed = 0
    errors: list[str] = []

    for mon in monitors:
        run = Run(monitor_id=mon.id, started_at=now)
        db.add(run)
        db.flush()

        try:
            status_code, html = fetch_product.fetch_html(
                mon.product_url,
                timeout_seconds=settings.fetch_timeout_seconds,
            )
            run.http_status = status_code
            if status_code >= 400:
                run.error_code = "http_error"
                run.finished_at = datetime.now(UTC)
                refresh_monitor_next_run(mon)
                db.commit()
                processed += 1
                errors.append(f"{mon.id}:http_{status_code}")
                continue

            parsed = extract_price.extract_from_html(html, mon.css_selector)
            if parsed is None:
                run.error_code = "parse_failed"
                run.raw_snippet = html[:2000]
                run.finished_at = datetime.now(UTC)
                refresh_monitor_next_run(mon)
                db.commit()
                processed += 1
                errors.append(f"{mon.id}:no_price")
                continue

            minor, currency, confidence, snippet = parsed
            run.parsed_price_minor = minor
            run.parsed_currency = currency
            run.parse_confidence = confidence
            run.raw_snippet = snippet[:2000]
            run.finished_at = datetime.now(UTC)

            db.add(
                PriceSnapshot(
                    monitor_id=mon.id,
                    run_id=run.id,
                    observed_at=datetime.now(UTC),
                    amount_minor=minor,
                    currency=currency,
                    confidence=confidence,
                )
            )

            prev = mon.last_price_minor
            mon.last_price_minor = minor
            mon.last_currency = currency

            reason = _notify_reason(prev, minor, mon.target_price_minor)
            if reason and mon.user and mon.user.email:
                day_iso = datetime.now(UTC).date().isoformat()
                dkey = _dedupe_key(str(mon.id), day_iso, reason, minor)
                existing = db.execute(
                    select(Notification.id).where(Notification.dedupe_key == dkey)
                ).scalar_one_or_none()
                if existing is None:
                    notif = Notification(
                        monitor_id=mon.id,
                        dedupe_key=dkey,
                        channel="email",
                        template_id="price_alert",
                        status="pending",
                    )
                    db.add(notif)
                    db.flush()
                    subject, body_html = _render_email(mon, prev, minor, currency, reason, settings)
                    try:
                        if settings.resend_api_key and settings.resend_from_email:
                            send_email(
                                api_key=settings.resend_api_key,
                                from_email=settings.resend_from_email,
                                to_email=mon.user.email,
                                subject=subject,
                                html=body_html,
                            )
                            notif.status = "sent"
                            notif.sent_at = datetime.now(UTC)
                        else:
                            notif.status = "skipped"
                            notif.error_detail = "Resend not configured"
                    except Exception as e:  # noqa: BLE001
                        logger.exception("Email send failed for monitor %s", mon.id)
                        notif.status = "failed"
                        notif.error_detail = str(e)[:2000]

            refresh_monitor_next_run(mon)
            db.commit()
            processed += 1
        except fetch_product.FetchError as e:
            run.error_code = e.code
            run.finished_at = datetime.now(UTC)
            refresh_monitor_next_run(mon)
            db.commit()
            processed += 1
            errors.append(f"{mon.id}:{e.code}")
        except Exception as e:  # noqa: BLE001
            logger.exception("Tick failed for monitor %s", mon.id)
            run.error_code = "internal_error"
            run.finished_at = datetime.now(UTC)
            refresh_monitor_next_run(mon)
            db.commit()
            processed += 1
            errors.append(f"{mon.id}:internal:{e!s}")

    return {
        "processed": processed,
        "due_candidates": len(monitors),
        "errors": errors,
    }


def _render_email(
    mon: Monitor,
    prev: int | None,
    new_minor: int,
    currency: str,
    reason: str,
    settings: Settings,
) -> tuple[str, str]:
    sym = {"USD": "$", "EUR": "€", "GBP": "£"}.get(currency, f"{currency} ")
    new_s = f"{sym}{new_minor / 100:.2f}"
    prev_s = f"{sym}{prev / 100:.2f}" if prev is not None else "—"
    base = (settings.app_public_url or "http://localhost:5173").rstrip("/")
    link = f"{base}/monitors"
    subj = f"Watchtower: price update — {mon.label or mon.product_url}"
    if reason == "first_price":
        subj = f"Watchtower: first price — {mon.label or 'monitor'}"
    elif reason == "price_drop":
        subj = f"Watchtower: price dropped — {mon.label or 'monitor'}"
    elif reason == "target_hit":
        subj = f"Watchtower: target price hit — {mon.label or 'monitor'}"

    html = f"""
    <p>Monitor: <strong>{mon.label or mon.product_url}</strong></p>
    <p>Previous: {prev_s} → New: <strong>{new_s}</strong> ({currency})</p>
    <p>Reason: {reason}</p>
    <p><a href="{link}">Open Watchtower</a></p>
    """
    return subj, html

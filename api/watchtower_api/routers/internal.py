from __future__ import annotations

from datetime import UTC, datetime
from secrets import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from watchtower_api.config import get_settings
from watchtower_api.db.session import get_db
from watchtower_api.models.monitor import Monitor, MonitorStatus

router = APIRouter(prefix="/internal", tags=["internal"])
_cron_bearer = HTTPBearer(auto_error=False)


def verify_cron_bearer(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_cron_bearer)],
) -> None:
    settings = get_settings()
    expected = settings.cron_bearer_token
    if not expected:
        raise HTTPException(status_code=503, detail="Cron is not configured")
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing cron bearer token")
    if not compare_digest(creds.credentials, expected):
        raise HTTPException(status_code=401, detail="Invalid cron bearer token")


@router.post("/jobs/tick", dependencies=[Depends(verify_cron_bearer)])
def jobs_tick(db: Annotated[Session, Depends(get_db)]) -> dict:
    """
    Scheduler entrypoint: list due monitors (v1 stub — no fetch/parse yet).
    """
    now = datetime.now(UTC)
    stmt = (
        select(func.count())
        .select_from(Monitor)
        .where(
            Monitor.status == MonitorStatus.ACTIVE.value,
            or_(Monitor.next_run_at.is_(None), Monitor.next_run_at <= now),
        )
    )
    due = int(db.execute(stmt).scalar_one())
    return {
        "due_monitors": due,
        "processed": 0,
        "message": "tick stub — scraping not wired",
    }

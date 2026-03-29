from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from watchtower_api.config import get_settings
from watchtower_api.db.session import get_db
from watchtower_api.routers.internal_auth import verify_cron_bearer
from watchtower_api.services.tick_runner import process_tick

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/jobs/tick", dependencies=[Depends(verify_cron_bearer)])
def jobs_tick(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int | None, Query(ge=1, le=100)] = None,
) -> dict:
    """
    Scheduler entrypoint: fetch/parse due monitors, write runs & snapshots, send email alerts.
    """
    settings = get_settings()
    lim = limit if limit is not None else settings.tick_default_limit
    return process_tick(db, settings, limit=lim)

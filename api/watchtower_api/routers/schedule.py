from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from watchtower_api.db.session import get_db
from watchtower_api.deps import get_current_user
from watchtower_api.models import User
from watchtower_api.schemas.schedule import ScheduleTranslateRequest, ScheduleTranslateResponse
from watchtower_api.services import cron_schedule
from watchtower_api.services.schedule_nl import natural_language_to_cron

router = APIRouter(prefix="/api/v1/schedule", tags=["schedule"])


@router.post("/translate", response_model=ScheduleTranslateResponse)
def translate_schedule(
    body: ScheduleTranslateRequest,
    _user: Annotated[User, Depends(get_current_user)],
    _db: Annotated[Session, Depends(get_db)],
) -> ScheduleTranslateResponse:
    """
    Best-effort NL → cron hint plus next fire time. If text is already a 5-field cron,
    it is validated and echoed back.
    """
    raw = body.text.strip()
    nl = natural_language_to_cron(raw)
    cron = nl or raw
    matched = nl is not None
    try:
        nxt = cron_schedule.next_run_utc(cron, body.timezone)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return ScheduleTranslateResponse(
        cron=cron,
        next_run_at=nxt,
        matched_natural_language=matched,
    )

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ScheduleTranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=512)
    timezone: str = "UTC"


class ScheduleTranslateResponse(BaseModel):
    cron: str
    next_run_at: datetime
    matched_natural_language: bool

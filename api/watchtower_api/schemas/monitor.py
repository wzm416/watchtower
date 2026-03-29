from __future__ import annotations

import uuid
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

from watchtower_api.models.monitor import MonitorStatus
from watchtower_api.services import cron_schedule


class MonitorCreate(BaseModel):
    label: str = ""
    product_url: str
    css_selector: str | None = None
    schedule_cron: str = Field(..., min_length=1, max_length=256)
    timezone: str = "UTC"
    status: str = MonitorStatus.ACTIVE.value
    target_price_minor: int | None = None

    @field_validator("schedule_cron")
    @classmethod
    def cron_valid(cls, v: str) -> str:
        s = v.strip()
        cron_schedule.next_run_utc(s, "UTC")
        return s

    @field_validator("timezone")
    @classmethod
    def timezone_valid(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError as e:
            raise ValueError("Unknown timezone") from e
        return v

    @field_validator("product_url")
    @classmethod
    def https_only(cls, v: str) -> str:
        s = v.strip()
        if not s.lower().startswith("https://"):
            raise ValueError("Only https:// product URLs are allowed")
        return s

    @field_validator("status")
    @classmethod
    def status_allowed(cls, v: str) -> str:
        if v not in (MonitorStatus.ACTIVE.value, MonitorStatus.PAUSED.value):
            raise ValueError("status must be active or paused")
        return v


class MonitorUpdate(BaseModel):
    label: str | None = None
    product_url: str | None = None
    css_selector: str | None = None
    schedule_cron: str | None = Field(default=None, min_length=1, max_length=256)
    timezone: str | None = None
    status: str | None = None
    target_price_minor: int | None = None
    next_run_at: datetime | None = None

    @field_validator("schedule_cron")
    @classmethod
    def cron_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        s = v.strip()
        cron_schedule.next_run_utc(s, "UTC")
        return s

    @field_validator("timezone")
    @classmethod
    def timezone_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError as e:
            raise ValueError("Unknown timezone") from e
        return v

    @field_validator("product_url")
    @classmethod
    def https_only(cls, v: str | None) -> str | None:
        if v is None:
            return v
        s = v.strip()
        if not s.lower().startswith("https://"):
            raise ValueError("Only https:// product URLs are allowed")
        return s

    @field_validator("status")
    @classmethod
    def status_allowed(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in (MonitorStatus.ACTIVE.value, MonitorStatus.PAUSED.value):
            raise ValueError("status must be active or paused")
        return v


class MonitorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    label: str
    product_url: str
    css_selector: str | None
    schedule_cron: str
    timezone: str
    status: str
    target_price_minor: int | None
    last_price_minor: int | None
    last_currency: str | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime

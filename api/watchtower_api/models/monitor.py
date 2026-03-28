from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from watchtower_api.db.base import Base

if TYPE_CHECKING:
    from watchtower_api.models.notification import Notification
    from watchtower_api.models.price_snapshot import PriceSnapshot
    from watchtower_api.models.run import Run
    from watchtower_api.models.user import User


class MonitorStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    label: Mapped[str] = mapped_column(String(512), default="")
    product_url: Mapped[str] = mapped_column(Text, nullable=False)
    css_selector: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    schedule_cron: Mapped[str] = mapped_column(String(256), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    status: Mapped[str] = mapped_column(String(16), default=MonitorStatus.ACTIVE.value)
    target_price_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_price_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship("User", back_populates="monitors")
    runs: Mapped[list[Run]] = relationship(
        "Run",
        back_populates="monitor",
        cascade="all, delete-orphan",
    )
    price_snapshots: Mapped[list[PriceSnapshot]] = relationship(
        "PriceSnapshot",
        back_populates="monitor",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification",
        back_populates="monitor",
        cascade="all, delete-orphan",
    )

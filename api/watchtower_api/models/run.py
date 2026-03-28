from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from watchtower_api.db.base import Base

if TYPE_CHECKING:
    from watchtower_api.models.monitor import Monitor
    from watchtower_api.models.price_snapshot import PriceSnapshot


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    monitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("monitors.id", ondelete="CASCADE"),
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_price_minor: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parsed_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parse_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    monitor: Mapped[Monitor] = relationship("Monitor", back_populates="runs")
    price_snapshot: Mapped[PriceSnapshot | None] = relationship(
        "PriceSnapshot",
        back_populates="run",
        uselist=False,
    )

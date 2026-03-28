from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from watchtower_api.db.session import get_db
from watchtower_api.deps import get_current_user
from watchtower_api.models import Monitor, User
from watchtower_api.schemas.monitor import MonitorCreate, MonitorRead, MonitorUpdate

router = APIRouter(prefix="/api/v1/monitors", tags=["monitors"])


def _owned_or_404(db: Session, user: User, monitor_id: UUID) -> Monitor:
    row = db.get(Monitor, monitor_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return row


@router.get("", response_model=list[MonitorRead])
def list_monitors(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Monitor]:
    stmt = select(Monitor).where(Monitor.user_id == user.id).order_by(Monitor.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("", response_model=MonitorRead, status_code=status.HTTP_201_CREATED)
def create_monitor(
    body: MonitorCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Monitor:
    mon = Monitor(
        user_id=user.id,
        label=body.label,
        product_url=body.product_url,
        css_selector=body.css_selector,
        schedule_cron=body.schedule_cron.strip(),
        timezone=body.timezone,
        status=body.status,
        target_price_minor=body.target_price_minor,
    )
    db.add(mon)
    db.commit()
    db.refresh(mon)
    return mon


@router.get("/{monitor_id}", response_model=MonitorRead)
def get_monitor(
    monitor_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Monitor:
    return _owned_or_404(db, user, monitor_id)


@router.patch("/{monitor_id}", response_model=MonitorRead)
def update_monitor(
    monitor_id: UUID,
    body: MonitorUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Monitor:
    mon = _owned_or_404(db, user, monitor_id)
    data = body.model_dump(exclude_unset=True)
    if "schedule_cron" in data and data["schedule_cron"] is not None:
        data["schedule_cron"] = str(data["schedule_cron"]).strip()
    for key, val in data.items():
        setattr(mon, key, val)
    db.commit()
    db.refresh(mon)
    return mon


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    mon = _owned_or_404(db, user, monitor_id)
    db.delete(mon)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

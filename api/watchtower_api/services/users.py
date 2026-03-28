from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from watchtower_api.models import User


def upsert_user_from_claims(db: Session, claims: dict[str, Any]) -> User:
    """Create or update a user from verified Google ID token claims."""
    sub = claims.get("sub")
    if not sub or not isinstance(sub, str):
        raise HTTPException(status_code=401, detail="Invalid token subject")

    email = claims.get("email")
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=401, detail="Email claim required")

    if not claims.get("email_verified", False):
        raise HTTPException(status_code=403, detail="Google email not verified")

    row = db.execute(select(User).where(User.google_sub == sub)).scalar_one_or_none()
    if row is None:
        row = User(google_sub=sub, email=email)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    if row.email != email:
        row.email = email
        db.commit()
        db.refresh(row)
    return row

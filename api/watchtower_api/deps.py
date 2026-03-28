from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from watchtower_api.config import get_settings
from watchtower_api.db.session import get_db
from watchtower_api.models import User
from watchtower_api.services.google_token import verify_google_id_token
from watchtower_api.services.users import upsert_user_from_claims

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    settings = get_settings()
    if not settings.google_audience_list:
        raise HTTPException(status_code=503, detail="Google auth is not configured")

    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")

    try:
        claims = verify_google_id_token(creds.credentials, settings.google_audience_list)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    return upsert_user_from_claims(db, claims)

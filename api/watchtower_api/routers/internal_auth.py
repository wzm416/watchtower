from __future__ import annotations

from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from watchtower_api.config import get_settings

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

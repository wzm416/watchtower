"""Verify Google Sign-In ID tokens (OAuth 2.0)."""

from __future__ import annotations

import base64
import json

from google.auth.transport import requests
from google.oauth2 import id_token


def _jwt_payload_json(token: str) -> dict:
    try:
        _header_b64, payload_b64, _sig_b64 = token.split(".")
    except ValueError as e:
        msg = "Invalid ID token"
        raise ValueError(msg) from e
    pad = "=" * (-len(payload_b64) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload_b64 + pad)
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, ValueError) as e:
        msg = "Invalid ID token"
        raise ValueError(msg) from e


def verify_google_id_token(token: str, allowed_audiences: list[str]) -> dict:
    """
    Validate signature, expiry, issuer, and audience against allowed OAuth client IDs.
    `allowed_audiences` is typically one or more Google OAuth 2.0 Client IDs (web).
    """
    if not allowed_audiences:
        msg = "No Google OAuth client IDs configured"
        raise ValueError(msg)

    unverified = _jwt_payload_json(token)
    aud = unverified.get("aud")
    if isinstance(aud, list):
        aud = next((a for a in aud if a in allowed_audiences), None)
    if not aud or aud not in allowed_audiences:
        msg = "Invalid ID token audience"
        raise ValueError(msg)

    return id_token.verify_oauth2_token(
        token,
        requests.Request(),
        audience=aud,
    )

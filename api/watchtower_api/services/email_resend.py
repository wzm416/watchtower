"""Send transactional email via Resend HTTP API."""

from __future__ import annotations

from typing import Any

import httpx


def send_email(
    *,
    api_key: str,
    from_email: str,
    to_email: str,
    subject: str,
    html: str,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    """POST /emails; returns JSON body. Raises on HTTP errors."""
    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=timeout_seconds) as client:
        r = client.post("https://api.resend.com/emails", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

"""Fetch product pages with basic SSRF guards."""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


@dataclass
class FetchError(Exception):
    code: str
    message: str


def _hostname_blocked(hostname: str) -> bool:
    if hostname in {"localhost"}:
        return True
    try:
        infos = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except OSError:
        return True
    for info in infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return True
    return False


def fetch_html(
    url: str,
    *,
    timeout_seconds: float = 10.0,
    max_bytes: int = 2_000_000,
) -> tuple[int, str]:
    """GET an https URL; return (status_code, text). Raises FetchError on errors."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise FetchError("invalid_scheme", "Only https URLs are allowed")
    host = parsed.hostname
    if not host:
        raise FetchError("invalid_url", "Missing host")
    if _hostname_blocked(host):
        raise FetchError("blocked_host", "Host resolves to a non-public address")

    headers = {
        "User-Agent": "WatchtowerPriceBot/1.0",
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    }
    try:
        client_kw = {"timeout": timeout_seconds, "follow_redirects": True, "max_redirects": 8}
        with httpx.Client(**client_kw) as client:
            resp = client.get(url, headers=headers)
    except httpx.HTTPError as e:
        raise FetchError("http_error", str(e)) from e

    if len(resp.content) > max_bytes:
        raise FetchError("too_large", "Response exceeded size limit")

    return resp.status_code, resp.text

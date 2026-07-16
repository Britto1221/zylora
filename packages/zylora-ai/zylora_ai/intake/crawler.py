from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx


class UnsafeUrlError(ValueError):
    pass


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeUrlError("Only absolute HTTP(S) URLs are supported.")
    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise UnsafeUrlError("Local addresses are not allowed.")
    try:
        addresses = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror as exc:
        raise UnsafeUrlError("The hostname could not be resolved.") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise UnsafeUrlError("Private or reserved network addresses are not allowed.")
    return url


def fetch_public_page(url: str, *, max_bytes: int = 1_000_000) -> str:
    validate_public_url(url)
    with httpx.Client(follow_redirects=True, timeout=15) as client:
        response = client.get(url, headers={"User-Agent": "ZyloraAuditBot/1.0"})
        response.raise_for_status()
        if "text/html" not in response.headers.get("content-type", ""):
            raise ValueError("The URL did not return HTML.")
        content = response.content[:max_bytes]
    return content.decode(response.encoding or "utf-8", errors="replace")

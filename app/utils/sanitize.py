from typing import Dict
from urllib.parse import urlparse

SENSITIVE_HEADERS = {"authorization", "proxy-authorization", "cookie", "set-cookie"}

def mask_headers(headers: Dict[str, str]) -> Dict[str, str]:
    safe = {}
    for k, v in headers.items():
        safe[k] = "***" if k.lower() in SENSITIVE_HEADERS else v
    return safe

def preview_body(content: bytes | None, limit: int = 2048) -> str:
    if not content:
        return ""
    head = content[:limit]
    try:
        return head.decode("utf-8", errors="replace")
    except Exception:
        return f"<{len(content)} bytes>"

def normalize_base(url: str | None) -> str | None:
    if not url:
        return None
    url = url.strip().rstrip("/")
    if not url:
        return None
    p = urlparse(url)
    if p.scheme in ("http", "https") and p.netloc:
        return url
    return None

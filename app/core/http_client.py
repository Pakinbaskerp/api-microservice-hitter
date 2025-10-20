import httpx
from .config import settings
from .logging import configure_logging
from ..utils.sanitize import mask_headers, preview_body

log = configure_logging()

async def _log_out_request(request: httpx.Request):
    rid = request.extensions.get("rid")
    body_preview = preview_body(request.content) if request.content else ""
    log.info(
        f"[RID:{rid}] → OUT {request.method} {request.url} "
        f"headers={mask_headers(dict(request.headers))}"
    )
    if body_preview:
        log.info(f"[RID:{rid}] → OUT body={body_preview}")

async def _log_in_response(response: httpx.Response):
    rid = response.request.extensions.get("rid")
    try:
        text = response.text[:2048]
    except Exception:
        text = f"<{len(response.content)} bytes>"
    log.info(
        f"[RID:{rid}] ← IN {response.status_code} for {response.request.method} {response.request.url} "
        f"headers={mask_headers(dict(response.headers))}"
    )
    if text:
        log.info(f"[RID:{rid}] ← IN body={text}")

def build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=settings.HTTPX_TIMEOUT_SECONDS,
        event_hooks={"request": [_log_out_request], "response": [_log_in_response]},
    )

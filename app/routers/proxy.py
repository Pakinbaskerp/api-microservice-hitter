from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
import httpx, uuid, time
from ..utils.sanitize import mask_headers, preview_body
from ..services.registry import registry
from ..core.logging import configure_logging

log = configure_logging()
router = APIRouter(prefix="/api", tags=["proxy"])

@router.api_route("/{service_name}/{path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD"])
async def proxy(service_name: str, path: str, request: Request):
    rid = uuid.uuid4().hex[:8]
    t0 = time.perf_counter()
    log.info(f"[RID:{rid}] ⇢ IN {request.method} /api/{service_name}/{path} "
             f"query={dict(request.query_params)} headers={mask_headers(dict(request.headers))}")

    base = registry.base_url(service_name)
    if not base:
        return PlainTextResponse(f"Service '{service_name}' not found.", status_code=404)

    url = f"{base}{path}"
    client: httpx.AsyncClient = request.app.state.http_client
    headers = dict(request.headers)
    body = await request.body()

    # Remove hop-by-hop headers
    for h in ["host", "content-length", "connection", "keep-alive",
              "proxy-authenticate", "proxy-authorization", "te",
              "trailers", "transfer-encoding", "upgrade"]:
        headers.pop(h, None)

    headers["X-Request-Id"] = rid

    try:
        if body:
            log.info(f"[RID:{rid}] ⇢ OUT {request.method} {url} body={preview_body(body)}")
        else:
            log.info(f"[RID:{rid}] ⇢ OUT {request.method} {url}")

        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=body,
            extensions={"rid": rid},
        )

        excluded = {"content-encoding","transfer-encoding","connection"}
        passthrough = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
        dt = (time.perf_counter() - t0) * 1000
        log.info(f"[RID:{rid}] ⇠ OUT {resp.status_code} ({dt:.1f} ms) {url}")
        return Response(content=resp.content, status_code=resp.status_code, headers=passthrough)
    except Exception as ex:
        log.exception(f"[RID:{rid}] Proxy error: {ex}")
        return PlainTextResponse(f"Proxy error: {ex}", status_code=500)

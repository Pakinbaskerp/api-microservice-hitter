from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, HTMLResponse, Response
from fastapi.openapi.docs import get_swagger_ui_html
import httpx, json
from ..services.registry import registry
from ..utils.sanitize import normalize_base

router = APIRouter(tags=["docs"])

def _server_url_for(request: Request) -> str:
    """
    Where Swagger 'Try it out' should call:
      - absolute: {API_GW_BASE}/api
      - relative: /api
    """
    base = getattr(request.app.state, "api_gw_base", None)
    return f"{base}/api" if base else "/api"

@router.get("/swagger/{service_name}")
async def swagger_through_gateway(service_name: str, request: Request):
    src = registry.src(service_name)
    if not src:
        return PlainTextResponse(f"Service '{service_name}' not found. See /services.", status_code=404)

    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.get(src)
        if r.status_code != 200:
            return PlainTextResponse(
                f"Failed to fetch downstream swagger ({r.status_code}) from {src}",
                status_code=502
            )
        data = r.json()
        # Make "Try it out" point to our gateway
        data["servers"] = [{"url": _server_url_for(request)}]
        return Response(json.dumps(data), media_type="application/json")

@router.get("/docs/{service_name}")
async def docs_for_service(service_name: str):
    if service_name not in registry.list():
        return PlainTextResponse(f"Service '{service_name}' not found. See /services.", status_code=404)
    return get_swagger_ui_html(
        openapi_url=f"/swagger/{service_name}",
        title=f"{service_name} API Docs (via Gateway)"
    )

@router.get("/")
async def home(request: Request):
    html_path = request.app.state.templates / "home.html"
    if not html_path.exists():
        return HTMLResponse("<h2>Missing app/templates/home.html</h2>", status_code=200)

    items = "".join([f'<li><a href="/docs/{name}">{name}</a></li>' for name in registry.list()])
    current = getattr(request.app.state, "api_gw_base", None) or "(relative: /api/{service})"
    gw_val = getattr(request.app.state, "api_gw_base", None) or ""

    html = html_path.read_text(encoding="utf-8")
    html = (html
            .replace("$items", items)
            .replace("$current", current)
            .replace("$gw", gw_val))
    return HTMLResponse(html)

@router.get("/set-gateway")
async def set_gateway(gateway: str = "", request: Request = None):
    request.app.state.api_gw_base = normalize_base(gateway)
    return RedirectResponse(url="/", status_code=303)

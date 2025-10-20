import json
from typing import Dict
from ..core.config import settings

SWAGGER_SUFFIX = "/swagger/v1/swagger.json"

class ServiceRegistry:
    def __init__(self):
        data = json.loads(settings.SERVICES_FILE.read_text(encoding="utf-8"))
        if "services" not in data or not isinstance(data["services"], dict):
            raise RuntimeError("services.json must have a top-level 'services' object")
        self._services: Dict[str, str] = data["services"]

    def list(self) -> list[str]:
        return list(self._services.keys())

    def src(self, name: str) -> str | None:
        return self._services.get(name)

    def base_url(self, name: str) -> str | None:
        """
        Convert .../swagger/v1/swagger.json -> upstream base ending with '/'
        """
        url = self._services.get(name)
        if not url:
            return None
        base = url[:-len(SWAGGER_SUFFIX)] if url.endswith(SWAGGER_SUFFIX) else url.rstrip("/")
        return base + "/"

registry = ServiceRegistry()

from __future__ import annotations

import threading
import time

import httpx
import uvicorn

from app.core.config import get_settings


def ensure_local_backend(timeout_seconds: float = 8.0) -> None:
    settings = get_settings()
    base_url = f"http://{settings.backend_host}:{settings.backend_port}"
    if _is_healthy(base_url):
        return

    thread = threading.Thread(target=_run_backend, name="smart-it-backend", daemon=True)
    thread.start()

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if _is_healthy(base_url):
            return
        time.sleep(0.2)


def _run_backend() -> None:
    from app.main import app

    settings = get_settings()
    config = uvicorn.Config(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level="warning",
        access_log=False,
    )
    uvicorn.Server(config).run()


def _is_healthy(base_url: str) -> bool:
    try:
        response = httpx.get(f"{base_url}/health", timeout=0.75)
        return response.status_code == 200
    except httpx.HTTPError:
        return False

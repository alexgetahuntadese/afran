from __future__ import annotations

import threading
import time
import traceback
from pathlib import Path

import httpx
import uvicorn

from app.core.config import get_settings


def ensure_local_backend(timeout_seconds: float = 8.0) -> None:
    settings = get_settings()
    base_url = f"http://{settings.backend_host}:{settings.backend_port}"
    if _is_healthy(base_url):
        return

    _log("Starting embedded backend")
    thread = threading.Thread(target=_run_backend, name="smart-it-backend", daemon=True)
    thread.start()

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if _is_healthy(base_url):
            _log("Embedded backend is healthy")
            return
        time.sleep(0.2)
    _log("Embedded backend did not become healthy before timeout")


def _run_backend() -> None:
    try:
        from app.main import app

        settings = get_settings()
        config = uvicorn.Config(
            app,
            host=settings.backend_host,
            port=settings.backend_port,
            log_level="warning",
            log_config=None,
            access_log=False,
        )
        uvicorn.Server(config).run()
    except Exception:
        _log(traceback.format_exc())


def _is_healthy(base_url: str) -> bool:
    try:
        response = httpx.get(f"{base_url}/health", timeout=0.75)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


def _log(message: str) -> None:
    try:
        with Path("smart_it_startup.log").open("a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")
    except OSError:
        pass

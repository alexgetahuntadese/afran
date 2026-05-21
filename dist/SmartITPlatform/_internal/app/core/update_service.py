from dataclasses import dataclass
from packaging.version import Version

import httpx


@dataclass(frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str
    update_available: bool
    installer_url: str | None
    sha256: str | None


class AutoUpdateService:
    def __init__(self, update_manifest_url: str) -> None:
        self.update_manifest_url = update_manifest_url

    async def check(self, current_version: str, license_key: str) -> UpdateInfo:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                self.update_manifest_url,
                headers={"X-License-Key": license_key},
            )
            response.raise_for_status()
            manifest = response.json()
        latest = str(manifest["version"])
        return UpdateInfo(
            current_version=current_version,
            latest_version=latest,
            update_available=Version(latest) > Version(current_version),
            installer_url=manifest.get("installer_url"),
            sha256=manifest.get("sha256"),
        )

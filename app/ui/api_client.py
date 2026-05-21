from dataclasses import dataclass

import httpx


@dataclass
class ApiSession:
    base_url: str = "http://127.0.0.1:8080"
    token: str | None = None
    organization_id: str | None = None

    @property
    def headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}


class ApiClient:
    def __init__(self, session: ApiSession) -> None:
        self.session = session

    def login(self, email: str, password: str) -> None:
        with httpx.Client(base_url=self.session.base_url, timeout=15) as client:
            response = client.post("/api/auth/login", json={"email": email, "password": password})
            response.raise_for_status()
            payload = response.json()
            self.session.token = payload["access_token"]
            self.session.organization_id = payload["organization_id"]

    def bootstrap(self, organization: str, name: str, email: str, password: str) -> None:
        with httpx.Client(base_url=self.session.base_url, timeout=15) as client:
            response = client.post(
                "/api/auth/bootstrap",
                json={
                    "organization_name": organization,
                    "branch_name": "Main Branch",
                    "email": email,
                    "full_name": name,
                    "password": password,
                },
            )
            response.raise_for_status()
            payload = response.json()
            self.session.token = payload["access_token"]
            self.session.organization_id = payload["organization_id"]

    def dashboard(self) -> dict:
        return self._get("/api/dashboard/summary")

    def devices(self) -> list[dict]:
        return self._get("/api/devices")

    def printers(self) -> list[dict]:
        return self._get("/api/printers")

    def alerts(self) -> list[dict]:
        return self._get("/api/alerts")

    def roi_report(self) -> dict:
        return self._get("/api/subscriptions/trial/roi-report")

    def _get(self, path: str):
        with httpx.Client(base_url=self.session.base_url, timeout=15, headers=self.session.headers) as client:
            response = client.get(path)
            response.raise_for_status()
            return response.json()

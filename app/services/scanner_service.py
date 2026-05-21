import ipaddress
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websocket_manager import websocket_manager
from app.alerts.alert_service import AlertService
from app.models import Branch, Device
from app.scanner.lan_scanner import LANScanner
from app.schemas.devices import DeviceCreate, ScanSummary
from app.services.device_service import DeviceService
from app.services.subscription_service import SubscriptionService


class ScannerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.scanner = LANScanner()
        self.devices = DeviceService(session)
        self.alerts = AlertService(session)
        self.subscriptions = SubscriptionService(session)

    async def scan_branch(self, organization_id: UUID, branch: Branch, subnet_cidr: str | None) -> ScanSummary:
        decision = await self.subscriptions.decision(organization_id, "scan")
        if not decision.allowed:
            raise PermissionError(decision.reason or "Scan is not allowed")

        cidr = subnet_cidr or branch.subnet_cidr or self._local_default_cidr()
        discovered = await self.scanner.scan(cidr)
        persisted: list[Device] = []

        for host in discovered:
            device = await self.devices.upsert_discovered(
                DeviceCreate(
                    organization_id=organization_id,
                    branch_id=branch.id,
                    ip_address=host.ip_address,
                    hostname=host.hostname,
                    mac_address=host.mac_address,
                    vendor=host.vendor,
                    operating_system=host.operating_system,
                    device_type=host.device_type,
                    status=host.status,
                    latency_ms=host.latency_ms,
                )
            )
            persisted.append(device)
            await self.alerts.evaluate_device(device)

        branch.subnet_cidr = cidr
        await self.session.commit()

        online = sum(1 for item in discovered if item.status.value == "online")
        departments = self._department_message(persisted)
        await websocket_manager.broadcast(
            organization_id,
            "scan.completed",
            {"branch_id": str(branch.id), "online_hosts": online, "message": departments},
        )
        return ScanSummary(
            branch_id=branch.id,
            scanned_hosts=ipaddress.ip_network(cidr, strict=False).num_addresses - 2,
            online_hosts=online,
            message=departments,
            devices=persisted,
        )

    def _local_default_cidr(self) -> str:
        return "192.168.1.0/24"

    def _department_message(self, devices: list[Device]) -> str:
        counts: dict[str, int] = {}
        for device in devices:
            department = device.department or "Network"
            counts[department] = counts.get(department, 0) + 1
        if not counts:
            return "No devices found on this scan"
        department, count = max(counts.items(), key=lambda item: item[1])
        return f"{count} devices found in {department} Department"

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websocket_manager import websocket_manager
from app.core.enums import AlertSeverity, AlertStatus, DeviceStatus
from app.models import Alert, Device, Printer
from app.repositories.alerts import AlertRepository
from app.schemas.alerts import AlertCreate


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AlertRepository(session)

    async def create(self, data: AlertCreate) -> Alert:
        alert = Alert(**data.model_dump())
        await self.repo.add(alert)
        await websocket_manager.broadcast(
            data.organization_id,
            "alert.created",
            {
                "id": str(alert.id),
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
            },
        )
        return alert

    async def acknowledge(self, alert_id: UUID, user_id: UUID) -> Alert:
        alert = await self.repo.get(alert_id)
        if alert is None:
            raise LookupError("Alert not found")
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now(UTC)
        await self.session.flush()
        return alert

    async def evaluate_device(self, device: Device) -> None:
        if device.status == DeviceStatus.OFFLINE:
            await self.create(
                AlertCreate(
                    organization_id=device.organization_id,
                    branch_id=device.branch_id,
                    device_id=device.id,
                    severity=AlertSeverity.CRITICAL,
                    title="PC disconnected" if device.device_type.value in {"pc", "laptop"} else "Device offline",
                    message=f"{device.hostname or device.ip_address} is offline.",
                    evidence={"ip_address": str(device.ip_address), "last_seen_at": str(device.last_seen_at)},
                )
            )
        elif device.latency_ms and device.latency_ms > 250:
            await self.create(
                AlertCreate(
                    organization_id=device.organization_id,
                    branch_id=device.branch_id,
                    device_id=device.id,
                    severity=AlertSeverity.WARNING,
                    title="Network instability detected",
                    message=f"{device.hostname or device.ip_address} latency is {device.latency_ms} ms.",
                    evidence={"latency_ms": device.latency_ms},
                )
            )

    async def evaluate_printer(self, printer: Printer) -> None:
        if printer.status.lower() in {"offline", "error", "paper_out", "spooler_stopped"}:
            await self.create(
                AlertCreate(
                    organization_id=printer.organization_id,
                    branch_id=printer.branch_id,
                    printer_id=printer.id,
                    severity=AlertSeverity.CRITICAL,
                    title="Printer offline detected",
                    message=f"{printer.name} requires attention: {printer.status}.",
                    evidence={"queue_depth": printer.queue_depth, "driver": printer.driver_name},
                )
            )

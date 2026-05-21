import csv
from io import BytesIO, StringIO
from uuid import UUID

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Device


class InventoryExportService:
    columns = [
        "hostname",
        "ip_address",
        "mac_address",
        "vendor",
        "operating_system",
        "device_type",
        "status",
        "assigned_user",
        "department",
        "floor",
        "last_seen_at",
        "notes",
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def csv_export(self, organization_id: UUID) -> str:
        devices = await self._devices(organization_id)
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=self.columns)
        writer.writeheader()
        for device in devices:
            writer.writerow(self._row(device))
        return buffer.getvalue()

    async def pdf_export(self, organization_id: UUID) -> bytes:
        devices = await self._devices(organization_id)
        buffer = BytesIO()
        page = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 48
        page.setFont("Helvetica-Bold", 14)
        page.drawString(48, y, "Device Inventory")
        y -= 28
        page.setFont("Helvetica", 8)
        for device in devices:
            line = (
                f"{device.hostname or '-'} | {device.ip_address} | {device.device_type.value} | "
                f"{device.status.value} | {device.department or '-'} | {device.assigned_user or '-'}"
            )
            page.drawString(48, y, line[:135])
            y -= 14
            if y < 48:
                page.showPage()
                page.setFont("Helvetica", 8)
                y = height - 48
        page.save()
        return buffer.getvalue()

    async def _devices(self, organization_id: UUID) -> list[Device]:
        result = await self.session.execute(
            select(Device).where(Device.organization_id == organization_id).order_by(Device.ip_address)
        )
        return list(result.scalars().all())

    def _row(self, device: Device) -> dict[str, str]:
        return {
            "hostname": device.hostname or "",
            "ip_address": str(device.ip_address),
            "mac_address": device.mac_address or "",
            "vendor": device.vendor or "",
            "operating_system": device.operating_system or "",
            "device_type": device.device_type.value,
            "status": device.status.value,
            "assigned_user": device.assigned_user or "",
            "department": device.department or "",
            "floor": device.floor or "",
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else "",
            "notes": device.notes or "",
        }

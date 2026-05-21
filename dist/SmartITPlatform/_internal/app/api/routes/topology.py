from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.core.enums import DeviceType
from app.models import Device, Printer, User

router = APIRouter(prefix="/topology", tags=["topology"])


@router.get("")
async def topology(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict:
    device_result = await session.execute(
        select(Device).where(Device.organization_id == user.organization_id)
    )
    printer_result = await session.execute(
        select(Printer).where(Printer.organization_id == user.organization_id)
    )
    devices = list(device_result.scalars().all())
    printers = list(printer_result.scalars().all())
    nodes = [
        {
            "id": str(device.id),
            "label": device.hostname or str(device.ip_address),
            "type": device.device_type.value,
            "status": device.status.value,
            "latency_ms": device.latency_ms,
        }
        for device in devices
    ]
    nodes.extend(
        {
            "id": str(printer.id),
            "label": printer.name,
            "type": "printer",
            "status": printer.status,
            "health_score": printer.health_score,
        }
        for printer in printers
    )
    gateways = [device for device in devices if device.device_type in {DeviceType.ROUTER, DeviceType.SWITCH}]
    gateway_id = str(gateways[0].id) if gateways else None
    edges = []
    if gateway_id:
        edges.extend({"source": gateway_id, "target": str(device.id)} for device in devices)
        edges.extend({"source": gateway_id, "target": str(printer.id)} for printer in printers)
    edges.extend(
        {"source": str(printer.assigned_device_id), "target": str(printer.id)}
        for printer in printers
        if printer.assigned_device_id
    )
    return {"nodes": nodes, "edges": edges}

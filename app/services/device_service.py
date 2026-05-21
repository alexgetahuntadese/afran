from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Device
from app.repositories.devices import DeviceRepository
from app.schemas.devices import DeviceCreate, DeviceUpdate
from app.services.subscription_service import SubscriptionService


class DeviceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = DeviceRepository(session)
        self.subscriptions = SubscriptionService(session)

    async def upsert_discovered(self, data: DeviceCreate) -> Device:
        device = await self.repo.find_by_ip(data.branch_id, data.ip_address)
        if device is None:
            await self.subscriptions.enforce_device_limit(data.organization_id)
            device = Device(**data.model_dump())
            await self.repo.add(device)
        else:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(device, key, value)
        if data.status.value == "online":
            device.last_seen_at = datetime.now(UTC)
        await self.session.flush()
        return device

    async def update(self, device_id: UUID, data: DeviceUpdate) -> Device:
        device = await self.repo.get(device_id)
        if device is None:
            raise LookupError("Device not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(device, key, value)
        await self.session.flush()
        return device

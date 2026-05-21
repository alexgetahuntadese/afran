from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import DeviceStatus
from app.models import Device
from app.repositories.base import Repository


class DeviceRepository(Repository[Device]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Device)

    async def list_by_branch(self, branch_id: UUID) -> list[Device]:
        return await self.list(select(Device).where(Device.branch_id == branch_id).order_by(Device.ip_address))

    async def list_by_org(self, organization_id: UUID) -> list[Device]:
        return await self.list(select(Device).where(Device.organization_id == organization_id))

    async def find_by_ip(self, branch_id: UUID, ip_address: str) -> Device | None:
        result = await self.session.execute(
            select(Device).where(Device.branch_id == branch_id, Device.ip_address == ip_address)
        )
        return result.scalar_one_or_none()

    async def count_online(self, organization_id: UUID) -> int:
        result = await self.session.execute(
            select(Device).where(
                Device.organization_id == organization_id,
                Device.status == DeviceStatus.ONLINE,
            )
        )
        return len(result.scalars().all())

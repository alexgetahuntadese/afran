from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertStatus
from app.models import Alert
from app.repositories.base import Repository


class AlertRepository(Repository[Alert]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Alert)

    async def open_for_org(self, organization_id: UUID) -> list[Alert]:
        return await self.list(
            select(Alert)
            .where(Alert.organization_id == organization_id, Alert.status == AlertStatus.OPEN)
            .order_by(Alert.created_at.desc())
        )

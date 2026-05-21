from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import RemoteSessionStatus
from app.models import RemoteSession
from app.schemas.remote_support import RemoteSessionCreate
from app.services.subscription_service import SubscriptionService


class RemoteSupportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.subscriptions = SubscriptionService(session)

    async def request_session(
        self, organization_id: UUID, technician_id: UUID, data: RemoteSessionCreate
    ) -> RemoteSession:
        decision = await self.subscriptions.decision(organization_id, "remote_support")
        if not decision.allowed:
            raise PermissionError(decision.reason or "Remote support is not allowed")
        limit_seconds = await self.subscriptions.remote_session_limit_seconds(organization_id)
        session = RemoteSession(
            organization_id=organization_id,
            technician_id=technician_id,
            device_id=data.device_id,
            status=RemoteSessionStatus.REQUESTED,
            max_duration_seconds=limit_seconds,
            audit_events={
                "events": [
                    {
                        "at": datetime.now(UTC).isoformat(),
                        "type": "permission_requested",
                        "message": "Secure remote support permission popup sent to endpoint agent.",
                    }
                ]
            },
        )
        self.session.add(session)
        await self.session.commit()
        return session

    async def approve(self, session_id: UUID, approved_by_user: str) -> RemoteSession:
        session = await self.session.get(RemoteSession, session_id)
        if session is None:
            raise LookupError("Remote session not found")
        session.status = RemoteSessionStatus.ACTIVE
        session.approved_by_user = approved_by_user
        session.started_at = datetime.now(UTC)
        session.audit_events.setdefault("events", []).append(
            {
                "at": session.started_at.isoformat(),
                "type": "approved",
                "message": f"Approved by {approved_by_user}",
            }
        )
        await self.session.commit()
        return session

    async def end(self, session_id: UUID) -> RemoteSession:
        session = await self.session.get(RemoteSession, session_id)
        if session is None:
            raise LookupError("Remote session not found")
        session.status = RemoteSessionStatus.ENDED
        session.ended_at = datetime.now(UTC)
        session.audit_events.setdefault("events", []).append(
            {"at": session.ended_at.isoformat(), "type": "ended", "message": "Session ended"}
        )
        await self.session.commit()
        return session

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertSeverity, DeviceStatus, PlanCode, SubscriptionStatus
from app.models import Alert, Device, Subscription
from app.repositories.subscriptions import SubscriptionRepository
from app.schemas.subscriptions import FeatureDecision, ROIReport


class SubscriptionService:
    PROFESSIONAL_FLAGS = {
        "unlimited_devices": True,
        "remote_support": True,
        "advanced_monitoring": True,
        "automation_scripts": True,
        "cloud_sync": False,
    }
    ENTERPRISE_FLAGS = {
        **PROFESSIONAL_FLAGS,
        "multi_branch": True,
        "analytics": True,
        "cloud_sync": True,
        "audit_logs": True,
        "ticket_system": True,
        "api_integrations": True,
        "backup_automation": True,
        "role_permissions": True,
        "sms_email_alerts": True,
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = SubscriptionRepository(session)

    async def decision(self, organization_id: UUID, feature: str) -> FeatureDecision:
        subscription = await self.repo.get_for_org(organization_id)
        if subscription is None:
            return FeatureDecision(allowed=False, reason="No subscription found", plan_code=PlanCode.PROFESSIONAL)

        if self._is_expired(subscription):
            subscription.status = SubscriptionStatus.EXPIRED
            await self.session.flush()
            return FeatureDecision(
                allowed=False,
                reason="Subscription expired. Renew to continue monitoring and remote support.",
                plan_code=subscription.plan_code,
            )

        if subscription.plan_code == PlanCode.TRIAL:
            allowed = feature in {"scan", "devices:read", "alerts:read", "printers:read", "remote_support"}
            if feature == "remote_support":
                allowed = True
            return FeatureDecision(
                allowed=allowed,
                reason=None if allowed else "Feature is not available on this plan",
                plan_code=subscription.plan_code,
            )

        flags = self.ENTERPRISE_FLAGS if subscription.plan_code == PlanCode.ENTERPRISE else self.PROFESSIONAL_FLAGS
        return FeatureDecision(
            allowed=bool(flags.get(feature, True)),
            reason=None,
            plan_code=subscription.plan_code,
        )

    async def enforce_device_limit(self, organization_id: UUID) -> None:
        subscription = await self.repo.get_for_org(organization_id)
        if not subscription or subscription.device_limit is None:
            return
        result = await self.session.execute(
            select(func.count(Device.id)).where(Device.organization_id == organization_id)
        )
        count = int(result.scalar_one())
        if count >= subscription.device_limit:
            raise PermissionError(f"This plan supports a maximum of {subscription.device_limit} devices")

    async def remote_session_limit_seconds(self, organization_id: UUID) -> int | None:
        subscription = await self.repo.get_for_org(organization_id)
        if not subscription:
            return 0
        if subscription.plan_code == PlanCode.TRIAL:
            return int(subscription.feature_flags.get("remote_support_minutes", 10)) * 60
        return None

    async def roi_report(self, organization_id: UUID) -> ROIReport:
        printer_interruptions = await self._count_alerts(organization_id, "printer")
        offline_devices = await self._count_devices(organization_id, DeviceStatus.OFFLINE)
        network_issues = await self._count_alerts(organization_id, "network")
        prevented = (printer_interruptions * 18) + (offline_devices * 12) + (network_issues * 20)
        return ROIReport(
            organization_id=organization_id,
            printer_interruptions=printer_interruptions,
            offline_devices=offline_devices,
            network_issues_detected=network_issues,
            estimated_downtime_minutes_prevented=prevented,
            headline="Your workspace found measurable IT risk before it became downtime.",
            upgrade_message="Keep monitoring and remote support active",
        )

    def _is_expired(self, subscription: Subscription) -> bool:
        now = datetime.now(UTC)
        if subscription.status != SubscriptionStatus.ACTIVE:
            return True
        if subscription.plan_code == PlanCode.TRIAL and subscription.trial_ends_at:
            return now > subscription.trial_ends_at
        if subscription.current_period_ends_at:
            return now > subscription.current_period_ends_at
        return False

    async def _count_alerts(self, organization_id: UUID, category: str) -> int:
        result = await self.session.execute(
            select(Alert).where(
                Alert.organization_id == organization_id,
                Alert.severity.in_([AlertSeverity.WARNING, AlertSeverity.CRITICAL]),
                Alert.title.ilike(f"%{category}%"),
            )
        )
        return len(result.scalars().all())

    async def _count_devices(self, organization_id: UUID, status: DeviceStatus) -> int:
        result = await self.session.execute(
            select(Device).where(Device.organization_id == organization_id, Device.status == status)
        )
        return len(result.scalars().all())

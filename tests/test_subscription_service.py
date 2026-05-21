from datetime import UTC, datetime, timedelta

from app.core.enums import PlanCode, SubscriptionStatus
from app.models import Subscription
from app.services.subscription_service import SubscriptionService


def test_expired_trial_is_blocked() -> None:
    service = SubscriptionService(session=None)  # type: ignore[arg-type]
    subscription = Subscription(
        plan_code=PlanCode.TRIAL,
        status=SubscriptionStatus.ACTIVE,
        trial_ends_at=datetime.now(UTC) - timedelta(days=1),
    )
    assert service._is_expired(subscription) is True


def test_active_trial_is_not_expired() -> None:
    service = SubscriptionService(session=None)  # type: ignore[arg-type]
    subscription = Subscription(
        plan_code=PlanCode.TRIAL,
        status=SubscriptionStatus.ACTIVE,
        trial_ends_at=datetime.now(UTC) + timedelta(days=1),
    )
    assert service._is_expired(subscription) is False

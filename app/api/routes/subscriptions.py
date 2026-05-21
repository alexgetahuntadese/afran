from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models import User
from app.schemas.subscriptions import FeatureDecision, ROIReport
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/feature/{feature}", response_model=FeatureDecision)
async def feature_decision(
    feature: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> FeatureDecision:
    return await SubscriptionService(session).decision(user.organization_id, feature)


@router.get("/trial/roi-report", response_model=ROIReport)
async def trial_roi_report(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ROIReport:
    return await SubscriptionService(session).roi_report(user.organization_id)

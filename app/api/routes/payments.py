from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_session
from app.core.enums import PaymentProvider
from app.models import Payment, User
from app.subscriptions.payment_providers import gateway_for

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentIntentRequest(BaseModel):
    provider: PaymentProvider
    amount: float
    currency: str = "ETB"


class PaymentIntentResponse(BaseModel):
    provider: PaymentProvider
    organization_id: UUID
    amount: float
    currency: str
    reference: str
    checkout_url: str | None


@router.post("/intent", response_model=PaymentIntentResponse)
async def create_intent(
    data: PaymentIntentRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> PaymentIntentResponse:
    intent = await gateway_for(data.provider).create_intent(
        user.organization_id,
        data.amount,
        data.currency,
    )
    session.add(
        Payment(
            organization_id=user.organization_id,
            provider=data.provider,
            external_reference=intent.reference,
            amount=data.amount,
            currency=data.currency,
            status="pending",
            raw_payload={"checkout_url": intent.checkout_url},
        )
    )
    await session.commit()
    return PaymentIntentResponse(**intent.__dict__)

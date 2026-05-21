from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.core.enums import PaymentProvider


@dataclass(frozen=True)
class PaymentIntent:
    provider: PaymentProvider
    organization_id: UUID
    amount: float
    currency: str
    reference: str
    checkout_url: str | None


class PaymentGateway(ABC):
    provider: PaymentProvider

    @abstractmethod
    async def create_intent(self, organization_id: UUID, amount: float, currency: str) -> PaymentIntent:
        raise NotImplementedError


class OfflineActivationGateway(PaymentGateway):
    def __init__(self, provider: PaymentProvider) -> None:
        self.provider = provider

    async def create_intent(self, organization_id: UUID, amount: float, currency: str) -> PaymentIntent:
        reference = f"{self.provider.value}-{organization_id.hex[:12]}"
        return PaymentIntent(
            provider=self.provider,
            organization_id=organization_id,
            amount=amount,
            currency=currency,
            reference=reference,
            checkout_url=None,
        )


def gateway_for(provider: PaymentProvider) -> PaymentGateway:
    return OfflineActivationGateway(provider)

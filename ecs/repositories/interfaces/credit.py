from typing import TYPE_CHECKING
from abc import ABC, abstractmethod



if TYPE_CHECKING:
    import uuid

    from sqlalchemy.ext.asyncio import AsyncSession
    from ecs.models.domain import CreditOffer, CreditAccount, RiskAssessment

class ICreditRepository(ABC):
    """Base abstract class for the credit repository"""

    @abstractmethod
    async def get_active_credit_offer(self, user_id: "uuid.UUID", db: "AsyncSession") -> "CreditOffer | None":
        ...

    @abstractmethod
    async def create_credit_offer(self, credit_offer: "CreditOffer", db: "AsyncSession") -> None:
        ...

    @abstractmethod
    async def create_credit_account(self, credit_account: "CreditAccount", db: "AsyncSession") -> None:
        ...

    @abstractmethod
    async def update_credit_offer_status(self, offer_id: "uuid.UUID", status: str, db: "AsyncSession") -> None:
        ...

    @abstractmethod
    async def create_risk_assessment(self, risk_assessment: "RiskAssessment", db: "AsyncSession") -> None:
        ...

    @abstractmethod
    async def get_valid_risk_assessment(self, user_id: "uuid.UUID", db: "AsyncSession") -> "RiskAssessment | None":
        ...
import uuid
from typing import Sequence
from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ecs.models.domain import Transaction

class ITransactionRepository(ABC):
    """Base abstract class for the transaction repository"""

    @abstractmethod
    async def get_recent_transactions(
        self, 
        user_id: uuid.UUID,
        db: AsyncSession, 
        since: datetime | None = None, 
        limit: int | None = None
    ) -> Sequence[Transaction]:
        ...

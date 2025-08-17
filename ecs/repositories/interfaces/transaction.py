import uuid
from typing import Sequence, TYPE_CHECKING
from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from ecs.models.domain import DBTransaction

class ITransactionRepository(ABC):
    """Base abstract class for the transaction repository"""

    @abstractmethod
    async def get_recent_transactions(
        self, 
        user_id: uuid.UUID,
        db: AsyncSession, 
        since: datetime | None = None, 
        limit: int | None = None
    ) -> Sequence["DBTransaction"]:
        ...

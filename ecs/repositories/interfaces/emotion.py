from abc import ABC, abstractmethod
from typing import Sequence, TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from ecs.models.domain import DBEmotionalEvent

class IEmotionalEventsRepository(ABC):
    """Base abstract class for the emotional events repository"""

    @abstractmethod
    async def ingest(self, events: Sequence["DBEmotionalEvent"], db: AsyncSession) -> None:
        ...

    @abstractmethod
    async def get_recent_emotional_events(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        since: datetime | None = None,
        limit: int | None = None
    ) -> Sequence["DBEmotionalEvent"]:
        ...
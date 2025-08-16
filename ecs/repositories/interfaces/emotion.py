from abc import ABC, abstractmethod
from typing import Sequence
from datetime import datetime
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from ecs.models.domain import EmotionalEvent

class IEmotionalEventsRepository(ABC):
    """Base abstract class for the emotional events repository"""

    @abstractmethod
    async def ingest(self, events: Sequence[EmotionalEvent], db: AsyncSession) -> None:
        ...

    @abstractmethod
    async def get_recent_emotional_events(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        since: datetime | None = None,
        limit: int | None = None
    ) -> Sequence[EmotionalEvent]:
        ...
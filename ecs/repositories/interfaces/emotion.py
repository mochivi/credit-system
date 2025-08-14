from abc import ABC, abstractmethod
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from ecs.models.domain import EmotionalEvent

class IEmotionalEventsRepository(ABC):
    """Base abstract class for EmotionalEventsRepository.
    Ensures protocol is followed
    """

    @abstractmethod
    async def ingest(self, events: Sequence[EmotionalEvent], db: AsyncSession):
        ...

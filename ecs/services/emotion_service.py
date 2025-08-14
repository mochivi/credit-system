from typing import Sequence

from ecs.models.schemas import EmotionalEvent
from ecs.models.domain import EmotionalEvent as DBEmotionalEvent
from ecs.services.dependencies import EmotionalEventsRepositoryDep
from ecs.core.db import AsyncSessionDep

class EmotionService:
    def __init__(self, emotional_events_repository: EmotionalEventsRepositoryDep, session: AsyncSessionDep) -> None:
        self.db = session
        self.emotional_events_repo = emotional_events_repository

    async def ingest(self, events: Sequence[EmotionalEvent]):
        db_events: list[DBEmotionalEvent] = [
            DBEmotionalEvent(**event.model_dump()) for event in events
        ]
        await self.emotional_events_repo.ingest(db_events, self.db)
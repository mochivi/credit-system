from datetime import datetime
from typing import Sequence, override
import uuid

import structlog
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ecs.repositories.interfaces import IEmotionalEventsRepository
from ecs.models.domain import EmotionalEvent
from ecs.repositories.exceptions import DatabaseError, EmotionalEventIngestionError

class EmotionalEventsRepository(IEmotionalEventsRepository):

    @override
    async def ingest(self, events: Sequence[EmotionalEvent], db: AsyncSession):
        logger = structlog.get_logger()
        
        logger.debug("Inserting emotional events")
        try:
            db.add_all(events)
        except IntegrityError as e:
            raise EmotionalEventIngestionError(
                f"Failed to insert emotional events: {e}",
                original_error=e
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {e}", original_error=e)

        logger.debug("Successfully inserted emotional events")

    @override
    async def get_recent_emotional_events(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
        since: datetime | None = None,
        limit: int | None = None
    ) -> Sequence[EmotionalEvent]:
        logger = structlog.get_logger()
        logger.debug("Retrieving recent emotional events", since=since.isoformat() if since else "ever")

        # Build query
        query = select(EmotionalEvent).where(EmotionalEvent.user_id == user_id)
        if since:
            query = query.where(EmotionalEvent.captured_at > since)
        if limit:
            query = query.limit(limit)
        query = query.order_by(EmotionalEvent.captured_at.desc())

        try:
            result = await db.execute(query)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {e}", original_error=e)

        # Extract EmotionalEvent objects from Row objects
        events = [row[0] for row in result.all()]
        if len(events) == 0:
            logger.warn(f"User has no emotional events since {since.isoformat() if since else "ever"}")
            return []

        logger.debug(f"Retrieved emotional events", count=len(events), since=since.isoformat() if since else "ever")
        return events
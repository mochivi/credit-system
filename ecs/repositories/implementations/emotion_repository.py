from typing import Sequence, override

import structlog
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
from typing import Sequence, override

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ecs.repositories.interfaces.emotion import IEmotionalEventsRepository
from ecs.models.domain import EmotionalEvent
from ecs.repositories.exceptions import EmotionalEventIngestionError

class EmotionalEventsRepository(IEmotionalEventsRepository):

    @override
    async def ingest(self, events: Sequence[EmotionalEvent], db: AsyncSession):
        logger = structlog.get_logger()
        
        try:
            db.add_all(events)
            await db.commit()
            logger.debug("Successfully inserted emotional events", count=len(events))
        except IntegrityError as e:
            await db.rollback()
            raise EmotionalEventIngestionError(
                f"Failed to insert emotional events: {e}",
                original_error=e,
                extra_context={"count": len(events)})
        except SQLAlchemyError:
            await db.rollback()
            raise
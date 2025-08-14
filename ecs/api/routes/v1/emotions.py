from fastapi import APIRouter, status
import structlog

from ecs.models.schemas.emotion import EmotionalEvent
from ecs.api.dependencies import ClientPrincipalDep, EmotionalEventsServiceDep

router = APIRouter(prefix="/emotions", tags=["Emotions"])

@router.post(
    path="/ingest",
    status_code=status.HTTP_200_OK,
    summary="Ingest emotional events",
)
async def ingest(
    events: list[EmotionalEvent],
    client: ClientPrincipalDep,
    emotional_events_service: EmotionalEventsServiceDep
) -> None:
    logger = structlog.get_logger()
    logger.info("Received ingest request")

    await emotional_events_service.ingest(events)
    
    logger.info("Succesfully processed ingest request")
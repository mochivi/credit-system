from fastapi import APIRouter, status

from ecs.models.schemas.emotion import EmotionalEvent

router = APIRouter(prefix="/emotions", tags=["Emotions"])

@router.post(
    path="/ingest",
    status_code=status.HTTP_200_OK,
    summary="Ingest emotional events",
)
def ingest(emotional_events: list[EmotionalEvent]) -> dict:
    return {"status": "processed"}
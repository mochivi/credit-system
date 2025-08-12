from fastapi import APIRouter, status

router = APIRouter(prefix="/healthz", tags=["Health"])

@router.get(
    path="/healthz",
    status_code=status.HTTP_200_OK,
    summary="Get app health status",
)
def get() -> dict:
    return {"status": "ok"}
import uuid

from fastapi import APIRouter, status

router = APIRouter(prefix="/credit", tags=["Credit"])


"""
Credit Limit API:
- Create a RESTful API endpoint that calculates and returns
    1) The ML model result. If the user was approved for a credit line
    2) The credit limit and interest rate
    3) Credit type (e.g., Short-Term, Long-Term)
The endpoint should accept relevant parameters and return the calculated credit limit and interest rate.
"""
@router.post(
    path="/apply",
    status_code=status.HTTP_200_OK,
    summary="Apply for credit line",
)
def apply():
    pass

"""
Triggers async job for applying credit limit and user notification
"""
@router.post(
    path="/offers/{offer_id}/accept",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept credit line offer",
)
def accept(offer_id: uuid.UUID):
    pass
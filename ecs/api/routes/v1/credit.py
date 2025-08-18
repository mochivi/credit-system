import uuid
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars
from fastapi import APIRouter, status

from ecs.api.dependencies import CurrentUserPrincipalDep, CreditServiceDep
from ecs.models.schemas import CreditOfferResponse, CreditAcceptResponse
from ecs.models.domain import DBCreditOffer
from ecs.services.exceptions import ActiveCreditOfferExistsError

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
    response_model=CreditOfferResponse
)
async def apply(
    user_token: CurrentUserPrincipalDep,
    credit_service: CreditServiceDep
) -> Any:
    logger = structlog.get_logger()
    logger.info("Received credit line apply request")

    user_id: uuid.UUID = uuid.UUID(user_token.sub)
    bind_contextvars(user_id=user_id)

    try:
        credit_offer: DBCreditOffer = await credit_service.apply_for_credit_line(user_id)
    except ActiveCreditOfferExistsError as e:
        logger.info("Returning valid credit offer")
        return e.credit_offer

    logger.info("Returning credit offer", offer_status=credit_offer.status)
    return credit_offer

"""
Triggers async job for applying credit limit and user notification
"""
@router.post(
    path="/offers/{offer_id}/accept",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept credit line offer",
)
async def accept(
    offer_id: uuid.UUID,
    user_token: CurrentUserPrincipalDep,
    credit_service: CreditServiceDep
) -> CreditAcceptResponse:
    logger = structlog.get_logger()
    logger.info("Received credit line apply request")

    user_id: uuid.UUID = uuid.UUID(user_token.sub)
    bind_contextvars(offer_id=offer_id, user_id=user_id)

    job_id: str = await credit_service.accept_credit_offer(offer_id, user_id)
    return CreditAcceptResponse(
        id=job_id,
        offer_id=str(offer_id),
        status="processing",
        message="Credit offer acceptance is being processed"
    )
import uuid
from typing import override
from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from structlog.contextvars import bind_contextvars

from ecs.models.schemas.credit import CreditOfferStatus
from ecs.repositories.interfaces import ICreditRepository
from ecs.repositories.exceptions import DatabaseError, NotFoundError
from ecs.models.domain import DBCreditOffer, DBCreditAccount, DBRiskAssessment

class CreditRepository(ICreditRepository):
    """Repository for credit-related database operations"""

    @override
    async def get_active_credit_offer(self, user_id: uuid.UUID, db: AsyncSession) -> DBCreditOffer | None:
        """Check if user has an active credit offer"""
        logger = structlog.get_logger()
        logger.debug("Checking for active credit offer", user_id=user_id)

        try:
            # Query for active credit offers (not expired, not accepted/rejected)
            query = select(DBCreditOffer).where(
                DBCreditOffer.user_id == user_id,
                DBCreditOffer.status == CreditOfferStatus.offered,
                datetime.now() < DBCreditOffer.expires_at,
            ).limit(1)
            
            result = await db.execute(query)
            active_offer = result.scalar_one_or_none()

            if not active_offer:
                return None
            
            bind_contextvars(offer_id=active_offer.id, offer_status=active_offer.status)
            logger.debug("Retrieved active credit offer")
            
            return active_offer
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error checking active credit offers: {e}", original_error=e)

    @override
    async def create_credit_offer(self, credit_offer: DBCreditOffer, db: AsyncSession) -> None:
        """Create a new credit offer"""
        logger = structlog.get_logger()
        logger.debug("Creating credit offer", user_id=credit_offer.user_id)

        try:
            db.add(credit_offer)
            await db.flush()  # Get the ID without committing
            await db.refresh(credit_offer)
            
            logger.debug("Credit offer created", offer_id=credit_offer.id, user_id=credit_offer.user_id)
            return
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error creating credit offer: {e}", original_error=e)

    @override
    async def create_credit_account(self, credit_account: DBCreditAccount, db: AsyncSession) -> None:
        """Create a new credit account"""
        logger = structlog.get_logger()
        logger.debug("Creating credit account", user_id=credit_account.user_id)

        try:
            db.add(credit_account)
            await db.flush()  # Get the ID without committing
            await db.refresh(credit_account)
            
            logger.debug("Credit account created", account_id=credit_account.id, user_id=credit_account.user_id)
            return
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error creating credit account: {e}", original_error=e)

    @override
    async def update_credit_offer_status(self, offer_id: uuid.UUID, status: str, db: AsyncSession) -> None:
        """Update credit offer status"""
        logger = structlog.get_logger()
        logger.debug("Updating credit offer status", offer_id=offer_id, status=status)

        try:
            query = select(DBCreditOffer).where(DBCreditOffer.id == offer_id)
            result = await db.execute(query)
            offer = result.scalar_one_or_none()
            
            if not offer:
                logger.warn("Credit offer not found for status update", offer_id=offer_id)
                raise NotFoundError(resource_type="Credit Offer", resource_id=offer_id)
            
            offer.status = status
            await db.flush()
            
            logger.debug("Credit offer status updated", offer_id=offer_id, status=status)
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error updating credit offer status: {e}", original_error=e)

    @override
    async def create_risk_assessment(self, risk_assessment: DBRiskAssessment, db: AsyncSession) -> None:
        """Create a new risk assessment"""
        logger = structlog.get_logger()
        logger.debug("Creating risk assessment", user_id=risk_assessment.user_id)

        try:
            db.add(risk_assessment)
            await db.flush()  # Get the ID without committing
            await db.refresh(risk_assessment)
            
            bind_contextvars(risk_assessment_id=risk_assessment.id, user_id=risk_assessment.user_id)
            logger.debug("Risk assessment created")
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error creating risk assessment: {e}", original_error=e)

    @override
    async def get_valid_risk_assessment(self, user_id: uuid.UUID, db: AsyncSession) -> DBRiskAssessment | None:
        """Get the most recent valid risk assessment for a user"""
        logger = structlog.get_logger()
        logger.debug("Getting valid risk assessment", user_id=user_id)

        try:
            # Query for the most recent risk assessment (within last 30 days)
            query = select(DBRiskAssessment).where(
                DBRiskAssessment.user_id == user_id,
                datetime.now() < DBRiskAssessment.expires_at 
            ).order_by(DBRiskAssessment.created_at.desc()).limit(1)
            
            result = await db.execute(query)
            risk_assessment = result.scalar_one_or_none()
            
            if not risk_assessment:
                logger.debug("No valid risk assessment found", user_id=user_id)
                return None
            
            bind_contextvars(risk_assessment_id=risk_assessment.id)
            logger.debug("Retrieved valid risk assessment")
            
            return risk_assessment
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error getting valid risk assessment: {e}", original_error=e)
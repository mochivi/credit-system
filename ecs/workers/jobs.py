import uuid
import structlog
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from structlog.contextvars import bind_contextvars
from ecs.core.config import settings
from ecs.models.domain import DBCreditOffer, DBCreditAccount
from ecs.models.schemas import CreditOfferStatus



def process_credit_acceptance(offer_id: str, user_id: str) -> None:
    """Background job to process credit offer acceptance"""
    logger = structlog.get_logger()
    bind_contextvars(offer_id=offer_id, user_id=user_id)
    logger.info("Processing credit acceptance")
    
    # Convert string IDs back to UUIDs
    offer_uuid = uuid.UUID(offer_id)
    user_uuid = uuid.UUID(user_id)
    
    # Create database connection for this job
    engine = create_engine(settings.DB_URL)
    SessionLocal = sessionmaker(bind=engine)
    
    try:
        with SessionLocal() as session:
            # Get the credit offer once more to ensure fresh data
            stmt = select(DBCreditOffer).where(
                DBCreditOffer.id == offer_uuid,
                DBCreditOffer.user_id == user_uuid,
                DBCreditOffer.status == CreditOfferStatus.offered
            )
            result = session.execute(stmt)
            credit_offer = result.scalar_one_or_none()
            
            if not credit_offer:
                logger.error("Credit offer not found or not in offered status")
                return
            
            # Check if user already has a credit account
            existing_account = session.execute(
                select(DBCreditAccount).where(DBCreditAccount.user_id == user_uuid)
            ).scalar_one_or_none()
            
            if existing_account:
                logger.error("User already has an active credit account", 
                    account_id=str(existing_account.id))
                return
            
            # Create credit account
            credit_account = DBCreditAccount(
                user_id=user_uuid,
                active_limit=credit_offer.credit_limit,
                apr=credit_offer.apr,
                credit_type=credit_offer.credit_type,
                current_balance=0,
                available_credit=credit_offer.credit_limit
            )
            
            # Update credit offer status to accepted
            credit_offer.status = CreditOfferStatus.accepted
            
            # Add and commit changes
            session.add(credit_account)
            session.commit()
            
            logger.info("Credit acceptance processed successfully", 
                account_id=str(credit_account.id))
            
    except Exception as e:
        logger.error("Failed to process credit acceptance", error=str(e))
        raise
    finally:
        engine.dispose()
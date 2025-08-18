import uuid
import structlog
import time
import datetime
from typing import Any

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

            # Send notification to user through specified channels
            notification_service = NotificationService("mock-service-url")
            notification_service.notify(user_id, "Your credit account has been created", ["push", "email"])
            
    except Exception as e:
        logger.error("Failed to process credit acceptance", error=str(e))
        raise
    finally:
        engine.dispose()    

class NotificationService:
    """Service for sending notifications through various channels."""
    
    def __init__(self, service_url: str, email_config: dict[str, Any] | None = None) -> None:
        """
        Initialize the notification service.
        
        Args:
            service_url: Base URL for notification services
            email_config: Email configuration dictionary with smtp_server, port, username, password
        """
        self.service_url = service_url
        self.email_config = email_config or {}
        self.logger = structlog.get_logger()
    
    def notify(self, user_id: str, message: str, notification_types: list[str] | None = None) -> dict[str, Any]:
        """
        Send notifications through specified channels.
        """
        self.logger.info("Sending notifications", user_id=user_id, types=notification_types)
        
        notification_types = notification_types or ["email"]
        success_count = 0
        results = {}
        
        if "email" in notification_types:
            result = self._notify_email(user_id, message)
            results["email"] = result
            if result:
                success_count+=1
        
        if "push" in notification_types:
            result = self._notify_push(user_id, message)
            results["push"] = result
            if result:
                success_count+=1
        
        # Process results
        result = {
            "success_count": success_count,
            "total_count": len(results),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        if success_count < len(results):
            self.logger.warning(
                "Some notifications failed", 
                success=success_count, 
                total=len(results)
            )
            
        return result
    
    def _notify_email(self, user_id: str, message: str) -> bool:
        """
        Send email notification.
        Placeholder
        """
        try:
            self.logger.info("Sending email notification")
            time.sleep(0.1)  # Simulate email sending
            self.logger.info("Email sent successfully")
            return True
        except Exception as e:
            self.logger.error("Failed to send email", error=str(e))
            raise
    
    def _notify_push(self, user_id: str, message: str) -> bool:
        """
        Send push notification.
        Placeholder
        """
        try:
            self.logger.info("Sending push notification", user_id=user_id)
            time.sleep(0.1)  # Simulate push notification
            self.logger.info("Push notification sent successfully", user_id=user_id)
            return True
        except Exception as e:
            self.logger.error("Failed to send push notification", user_id=user_id, error=str(e))
            raise
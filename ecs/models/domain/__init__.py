from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the domain."""
    pass

from ecs.models.domain.user import User
from ecs.models.domain.emotion import EmotionalEvent
from ecs.models.domain.transactions import Transaction
from ecs.models.domain.credit import RiskAssessment, CreditOffer, CreditAccount
from ecs.models.domain.client import Client

__all__ = [
    "Base",
    "User",
    "Client",
    "EmotionalEvent", 
    "Transaction",
    "RiskAssessment",
    "CreditOffer", 
    "CreditAccount",
]
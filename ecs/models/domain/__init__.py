from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the domain."""
    pass

from .user import User
from .emotion import EmotionalEvent
from .transactions import Transaction
from .credit import RiskAssessment, CreditOffer, CreditAccount

__all__ = [
    "Base",
    "User",
    "EmotionalEvent", 
    "Transaction",
    "RiskAssessment",
    "CreditOffer", 
    "CreditAccount"
]
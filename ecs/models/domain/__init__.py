from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models in the domain."""
    pass

from ecs.models.domain.user import DBUser
from ecs.models.domain.emotion import DBEmotionalEvent
from ecs.models.domain.transactions import DBTransaction
from ecs.models.domain.credit import DBRiskAssessment, DBCreditOffer, DBCreditAccount
from ecs.models.domain.client import DBClient

__all__ = [
    "Base",
    "DBUser",
    "DBClient",
    "DBEmotionalEvent", 
    "DBTransaction",
    "DBRiskAssessment",
    "DBCreditOffer", 
    "DBCreditAccount",
]
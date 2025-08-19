import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from rq import Queue

from ecs.models.schemas import (
    Features, RiskAssessment, CreditOffer, CreditOfferStatus, 
    CreditType
)
from ecs.models.domain import DBRiskAssessment, DBCreditOffer
from ecs.repositories import CreditRepository, TransactionRepository, EmotionalEventsRepository
from ecs.services.internal import FeatureEngineeringService, CreditModelService


@pytest.fixture
def user_id():
    """Generate a fixed test user ID."""
    return uuid.UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def offer_id():
    """Generate a fixed test offer ID."""
    return uuid.UUID("87654321-8765-4321-8765-432187654321")


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    
    # Configure the session to return itself from methods like __aenter__
    session.__aenter__.return_value = session
    
    # Return a method that can be awaited
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_redis_queue():
    """Create a mock Redis queue."""
    queue = MagicMock(spec=Queue)
    queue.enqueue.return_value = "job-id"
    return queue


@pytest.fixture
def mock_credit_repository():
    """Create a mock credit repository."""
    repo = AsyncMock(spec=CreditRepository)
    return repo


@pytest.fixture
def mock_transaction_repository():
    """Create a mock transaction repository."""
    repo = AsyncMock(spec=TransactionRepository)
    repo.get_recent_transactions.return_value = []
    return repo


@pytest.fixture
def mock_emotional_events_repository():
    """Create a mock emotional events repository."""
    repo = AsyncMock(spec=EmotionalEventsRepository)
    repo.get_recent_emotional_events.return_value = []
    return repo


@pytest.fixture
def mock_feature_engineering_service():
    """Create a mock feature engineering service."""
    service = AsyncMock(spec=FeatureEngineeringService)
    service.transactions_since = datetime.now() - timedelta(days=90)
    service.transaction_limit = 1000
    service.emotional_events_since = datetime.now() - timedelta(days=90)
    service.emotional_events_limit = 1000
    
    # Set up the create_features method
    service.create_features.return_value = Features(
        average_daily_spend=100.0,
        avg_daily_transactions=5,
        max_single_transaction=500.0,
        income_volatility=0.2,
        average_emotional_stability=0.7,
        stress_events_count=10,
        positive_emotion_ratio=0.6,
        emotional_volatility=0.3,
        recent_emotional_trend=0.5,
        spending_pattern_change=0.1,
        emotional_spending_correlation=0.3
    )
    return service


@pytest.fixture
def mock_credit_model_service():
    """Create a mock credit model service."""
    service = AsyncMock(spec=CreditModelService)
    service.predict_credit_risk.return_value = RiskAssessment(risk_score=0.3)
    return service


@pytest.fixture
def sample_features():
    """Create sample features for testing."""
    return Features(
        average_daily_spend=100.0,
        avg_daily_transactions=5,
        max_single_transaction=500.0,
        income_volatility=0.2,
        average_emotional_stability=0.7,
        stress_events_count=10,
        positive_emotion_ratio=0.6,
        emotional_volatility=0.3,
        recent_emotional_trend=0.5,
        spending_pattern_change=0.1,
        emotional_spending_correlation=0.3
    )


@pytest.fixture
def sample_risk_assessment_low():
    """Create a sample low-risk assessment."""
    return RiskAssessment(risk_score=0.2)


@pytest.fixture
def sample_risk_assessment_medium():
    """Create a sample medium-risk assessment."""
    return RiskAssessment(risk_score=0.6)


@pytest.fixture
def sample_risk_assessment_high():
    """Create a sample high-risk assessment."""
    return RiskAssessment(risk_score=0.8)


@pytest.fixture
def sample_db_risk_assessment(user_id):
    """Create a sample DB risk assessment."""
    return DBRiskAssessment(
        id=uuid.uuid4(),
        user_id=user_id,
        risk_score=0.3,
        expires_at=datetime.now() + timedelta(days=15)
    )


@pytest.fixture
def sample_credit_offer():
    """Create a sample credit offer."""
    return CreditOffer(
        status=CreditOfferStatus.offered,
        credit_type=CreditType.long_term,
        credit_limit=10000.0,
        apr=0.15
    )


@pytest.fixture
def sample_db_credit_offer(user_id, offer_id):
    """Create a sample DB credit offer."""
    return DBCreditOffer(
        id=offer_id,
        user_id=user_id,
        risk_assessment_id=uuid.uuid4(),
        credit_type=CreditType.long_term,
        credit_limit=Decimal("10000.00"),
        apr=Decimal("0.15"),
        status=CreditOfferStatus.offered,
        expires_at=datetime.now() + timedelta(days=15)
    )

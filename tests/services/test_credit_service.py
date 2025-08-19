import uuid
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from ecs.services.credit_service import CreditService
from ecs.models.schemas import CreditOffer, CreditOfferStatus, CreditType
from ecs.models.domain import DBCreditOffer
from ecs.services.exceptions import (
    ActiveCreditOfferExistsError, CreditAccountExistsError, 
    NoActiveCreditOfferExistsError, InvalidCreditOfferError
)


class TestCreditService:
    
    @pytest.fixture
    def credit_service(
        self,
        mock_credit_repository,
        mock_transaction_repository,
        mock_emotional_events_repository,
        mock_feature_engineering_service,
        mock_credit_model_service,
        mock_db_session,
        mock_redis_queue
    ):
        """Create an instance of the CreditService with mocked dependencies."""
        return CreditService(
            credit_repository=mock_credit_repository,
            transaction_repository=mock_transaction_repository,
            emotional_events_repo=mock_emotional_events_repository,
            feature_engineering_service=mock_feature_engineering_service,
            credit_model_service=mock_credit_model_service,
            session=mock_db_session,
            redis_queue=mock_redis_queue
        )
    
    async def test_apply_for_credit_line_success_new_assessment(
        self,
        credit_service,
        mock_credit_repository,
        mock_transaction_repository,
        mock_emotional_events_repository,
        mock_feature_engineering_service,
        mock_credit_model_service,
        mock_db_session,
        user_id,
        sample_features
    ):
        """Test successful credit line application with new risk assessment."""
        # Configure mocks
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = None
        mock_credit_repository.get_valid_risk_assessment.return_value = None
        mock_credit_repository.create_credit_offer.return_value = None
        
        # Mock the calculator
        with patch("ecs.services.credit_service.CreditOfferCalculator") as mock_calculator_class:
            mock_calculator = mock_calculator_class.return_value
            mock_calculator.calculate_offer.return_value = CreditOffer(
                status=CreditOfferStatus.offered,
                credit_type=CreditType.long_term,
                credit_limit=10000.0,
                apr=0.15
            )
            
            # Execute the method
            _ = await credit_service.apply_for_credit_line(user_id)
            
            # Verify interactions
            mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
            mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)
            mock_transaction_repository.get_recent_transactions.assert_called_once()
            mock_emotional_events_repository.get_recent_emotional_events.assert_called_once()
            mock_feature_engineering_service.create_features.assert_called_once()
            mock_credit_model_service.predict_credit_risk.assert_called_once_with(sample_features)
            mock_credit_repository.create_risk_assessment.assert_called_once()
            mock_calculator.calculate_offer.assert_called_once()
            mock_credit_repository.create_credit_offer.assert_called_once()
            mock_db_session.commit.assert_called_once()
    
    async def test_apply_for_credit_line_success_existing_assessment(
        self,
        credit_service,
        mock_credit_repository,
        mock_transaction_repository,
        mock_emotional_events_repository,
        mock_feature_engineering_service,
        mock_credit_model_service,
        mock_db_session,
        user_id,
        sample_db_risk_assessment,
        sample_features
    ):
        """Test successful credit line application with existing risk assessment."""
        # Configure mocks
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = None
        mock_credit_repository.get_valid_risk_assessment.return_value = sample_db_risk_assessment
        mock_credit_repository.create_credit_offer.return_value = None
        
        # Mock the calculator
        with patch("ecs.services.credit_service.CreditOfferCalculator") as mock_calculator_class:
            mock_calculator = mock_calculator_class.return_value
            mock_calculator.calculate_offer.return_value = CreditOffer(
                status=CreditOfferStatus.offered,
                credit_type=CreditType.long_term,
                credit_limit=10000.0,
                apr=0.15
            )
            
            # Execute the method
            result = await credit_service.apply_for_credit_line(user_id)
            
            # Verify interactions
            mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
            mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)
            mock_transaction_repository.get_recent_transactions.assert_called_once()
            mock_emotional_events_repository.get_recent_emotional_events.assert_called_once()
            mock_feature_engineering_service.create_features.assert_called_once()
            mock_credit_model_service.predict_credit_risk.assert_not_called()  # Should not be called when we have existing assessment
            mock_credit_repository.create_risk_assessment.assert_not_called()  # Should not be called when we have existing assessment
            mock_calculator.calculate_offer.assert_called_once()
            mock_credit_repository.create_credit_offer.assert_called_once()
            mock_db_session.commit.assert_called_once()
    
    async def test_apply_for_credit_line_active_account_exists(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        user_id
    ):
        """Test credit line application when user already has an active credit account."""
        # Configure mocks to simulate active credit account
        mock_credit_repository.get_credit_account_for_user.return_value = MagicMock()
        
        # Execute the method and check for expected exception
        with pytest.raises(CreditAccountExistsError):
            await credit_service.apply_for_credit_line(user_id)
            
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_not_called()
    
    async def test_apply_for_credit_line_active_offer_exists(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        user_id,
        sample_db_credit_offer
    ):
        """Test credit line application when user already has an active credit offer."""
        # Configure mocks to simulate active credit offer
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = sample_db_credit_offer
        
        # Execute the method and check for expected exception
        with pytest.raises(ActiveCreditOfferExistsError) as excinfo:
            await credit_service.apply_for_credit_line(user_id)
            
        # Verify the exception details
        assert excinfo.value.credit_offer == sample_db_credit_offer
        
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)
    
    async def test_apply_for_credit_line_exception_handling(
        self,
        credit_service,
        mock_credit_repository,
        mock_transaction_repository,
        mock_emotional_events_repository,
        mock_feature_engineering_service,
        mock_credit_model_service,
        mock_db_session,
        user_id
    ):
        """Test exception handling during credit line application."""
        # Configure mocks
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = None
        mock_credit_repository.get_valid_risk_assessment.return_value = None
        
        # Make create_risk_assessment raise an exception
        mock_credit_repository.create_risk_assessment.side_effect = Exception("Database error")
        
        # Execute the method and check for exception propagation
        with pytest.raises(Exception):
            await credit_service.apply_for_credit_line(user_id)
            
        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()
    
    async def test_accept_credit_offer_success(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        mock_redis_queue,
        user_id,
        offer_id,
        sample_db_credit_offer
    ):
        """Test successful credit offer acceptance."""
        # Configure mocks
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = sample_db_credit_offer
        
        # Execute the method
        job_id = await credit_service.accept_credit_offer(offer_id, user_id)
        
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_redis_queue.enqueue.assert_called_once()
        
        # Check the job ID format (should be UUID)
        assert uuid.UUID(job_id, version=4)
    
    async def test_accept_credit_offer_with_active_account(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        user_id,
        offer_id
    ):
        """Test credit offer acceptance when user already has an active credit account."""
        # Configure mocks to simulate active credit account
        mock_credit_repository.get_credit_account_for_user.return_value = MagicMock()
        
        # Execute the method and check for expected exception
        with pytest.raises(CreditAccountExistsError):
            await credit_service.accept_credit_offer(offer_id, user_id)
            
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_not_called()
    
    async def test_accept_credit_offer_no_active_offer(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        user_id,
        offer_id
    ):
        """Test credit offer acceptance when no active offer exists."""
        # Configure mocks to simulate no active offer
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = None
        
        # Execute the method and check for expected exception
        with pytest.raises(NoActiveCreditOfferExistsError):
            await credit_service.accept_credit_offer(offer_id, user_id)
            
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)
    
    async def test_accept_credit_offer_id_mismatch(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        user_id,
        offer_id,
        sample_db_credit_offer
    ):
        """Test credit offer acceptance with mismatched offer IDs."""
        # Configure mocks with a different offer ID than requested
        different_offer = sample_db_credit_offer
        different_offer.id = uuid.uuid4()  # Different ID than offer_id fixture
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = different_offer
        
        # Execute the method and check for expected exception
        with pytest.raises(InvalidCreditOfferError):
            await credit_service.accept_credit_offer(offer_id, user_id)
            
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)
    
    async def test_accept_credit_offer_expired(
        self,
        credit_service,
        mock_credit_repository,
        mock_db_session,
        user_id,
        offer_id
    ):
        """Test credit offer acceptance with expired offer."""
        # Configure mocks with an expired offer
        expired_offer = MagicMock(spec=DBCreditOffer)
        expired_offer.id = offer_id
        expired_offer.expires_at = datetime.now() - timedelta(days=1)  # Expired
        
        mock_credit_repository.get_credit_account_for_user.return_value = None
        mock_credit_repository.get_active_credit_offer_for_user.return_value = expired_offer
        
        # Execute the method and check for expected exception
        with pytest.raises(InvalidCreditOfferError):
            await credit_service.accept_credit_offer(offer_id, user_id)
            
        # Verify interactions
        mock_credit_repository.get_credit_account_for_user.assert_called_once_with(user_id, mock_db_session)
        mock_credit_repository.get_active_credit_offer_for_user.assert_called_once_with(user_id, mock_db_session)

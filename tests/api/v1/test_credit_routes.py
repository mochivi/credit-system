from unittest.mock import patch

from fastapi import status
from ecs.models.schemas import CreditOfferStatus, CreditType
from ecs.services.exceptions import (
    ActiveCreditOfferExistsError, NoActiveCreditOfferExistsError, InvalidCreditOfferError,
    CreditAccountExistsError)


class TestCreditRoutes:
    """Tests for the credit API endpoints."""
    
    @patch("ecs.services.credit_service.CreditService.apply_for_credit_line")
    async def test_apply_for_credit_success(
        self,
        mock_apply_for_credit_line,
        test_client,
        auth_headers,
        sample_db_credit_offer,
        user_id,
    ):
        """Test successful application for credit line."""
        mock_apply_for_credit_line.return_value = sample_db_credit_offer
        
        response = test_client.post(
            "/api/v1/credit/apply",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["status"] == CreditOfferStatus.offered
        assert result["credit_type"] == CreditType.long_term
        
        # Verify service was called
        mock_apply_for_credit_line.assert_called_once()
        
    @patch("ecs.services.credit_service.CreditService.apply_for_credit_line")
    async def test_apply_for_credit_with_existing_offer(
        self,
        mock_apply_for_credit_line,
        test_client,
        auth_headers,
        sample_db_credit_offer,
    ):
        """Test application with existing credit offer."""
        error = ActiveCreditOfferExistsError(
            credit_offer=sample_db_credit_offer,
            message="User already has an active credit offer"
        )
        mock_apply_for_credit_line.side_effect = error
        
        response = test_client.post(
            "/api/v1/credit/apply",
            headers=auth_headers
        )
        
        # Assert - should return the existing offer
        assert response.status_code == status.HTTP_200_OK
    
    @patch("ecs.services.credit_service.CreditService.apply_for_credit_line")
    async def test_apply_for_credit_with_existing_credit_account(
        self,
        mock_apply_for_credit_line,
        test_client,
        auth_headers,
    ):
        """Test application with existing credit offer."""
        error = CreditAccountExistsError(
            message="User already has an active credit account"
        )
        mock_apply_for_credit_line.side_effect = error
        
        response = test_client.post(
            "/api/v1/credit/apply",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        
    async def test_apply_for_credit_unauthenticated(
        self,
        test_client,
    ):
        """Test credit application without authentication."""
        response = test_client.post("/api/v1/credit/apply")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("ecs.services.credit_service.CreditService.accept_credit_offer")
    async def test_accept_credit_offer_success(
        self,
        mock_accept_credit_offer,
        test_client,
        auth_headers,
        offer_id,
    ):
        """Test successful credit offer acceptance."""
        job_id = "test-job-id"
        mock_accept_credit_offer.return_value = job_id
        
        response = test_client.post(
            f"/api/v1/credit/offers/{offer_id}/accept",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        result = response.json()
        assert result["id"] == job_id
        assert result["offer_id"] == str(offer_id)
        assert result["status"] == "processing"
        
    @patch("ecs.services.credit_service.CreditService.accept_credit_offer")
    async def test_accept_credit_offer_no_active_offer(
        self,
        mock_accept_credit_offer,
        test_client,
        auth_headers,
        offer_id,
    ):
        """Test credit offer acceptance with no active offer."""
        error_message = "No active credit offer found"
        mock_accept_credit_offer.side_effect = NoActiveCreditOfferExistsError(error_message)
        
        response = test_client.post(
            f"/api/v1/credit/offers/{offer_id}/accept",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("ecs.services.credit_service.CreditService.accept_credit_offer")
    async def test_accept_credit_offer_with_existing_credit_account(
        self,
        mock_accept_credit_offer,
        test_client,
        auth_headers,
        offer_id
    ):
        """Test application with existing credit offer."""
        mock_accept_credit_offer.side_effect = CreditAccountExistsError(
            message="User already has an active credit account"
        )
        
        response = test_client.post(
            "/api/v1/credit/apply",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        
    async def test_accept_credit_offer_unauthenticated(
        self,
        test_client,
        offer_id,
    ):
        """Test credit offer acceptance without authentication."""
        # Act
        response = test_client.post(
            f"/api/v1/credit/offers/{offer_id}/accept"
        )
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
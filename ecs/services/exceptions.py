from typing import override, Any, TYPE_CHECKING

from ecs.core.exceptions import BaseError

if TYPE_CHECKING:
    from ecs.models.domain.credit import DBCreditOffer

class BaseServiceError(BaseError):
    """Base exception class for all service errors"""
    pass

class BusinessLogicError(BaseServiceError):
    """Business logic validation error"""

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        pass

class ActiveCreditOfferExistsError(BusinessLogicError):
    """Active credit offer already exists"""

    def __init__(self, credit_offer: "DBCreditOffer", message: str, **kwargs) -> None:
        self.credit_offer = credit_offer
        super().__init__(message, **kwargs)

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        result["credit_offer"] = self.credit_offer
        return super()._add_subclass_fields(result)

class NoActiveCreditOfferExistsError(BusinessLogicError):
    """No active credit offer exists"""
    pass

class InvalidCreditOfferError(BusinessLogicError):
    """User provided offer_id does not match id of current active offer"""
    pass

class ExpiredCreditOfferError(BusinessLogicError):
    """User provided offer_id does not match id of current active offer"""
    pass

class CreditAccountExistsError(BusinessLogicError):
    """User already has a credit account"""
    pass

class UnauthorizedError(BaseServiceError):
    """Unauthorized action error"""

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        pass

class ForbiddenError(BaseServiceError):
    """Forbidden action error"""

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        pass
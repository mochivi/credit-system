from typing import override, Any

from ecs.core.exceptions import BaseError

class BaseServiceError(BaseError):
    """Base exception class for all service errors"""
    pass

class BusinessLogicError(BaseServiceError):
    """Business logic validation error"""
    
    def __init__(
        self,
        message: str,
        original_error: Exception | None = None,
        **kwargs
    ) -> None:
        super().__init__(message, original_error=original_error, **kwargs)

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
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
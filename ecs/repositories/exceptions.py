import uuid
from typing import Any, override

from ecs.core.exceptions import BaseError

class BaseDomainError(BaseError):
    """Base error class for all domain errors"""
    pass


# For the current moment, this can be used as a generic database error
class DatabaseError(BaseError):
    """Base error class for all database operational errors"""
    pass

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        pass

# Generic errors

class NotFoundError(BaseDomainError):
    """Generic resource not found exception"""
    
    def __init__(
        self, 
        resource_type: str | None = None, 
        resource_id: uuid.UUID | None = None,
        message: str | None = None,
        extra_context: dict[str, Any] | None = None,
        **kwargs
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.message = message or f"{resource_type} with id {resource_id} not found"
        super().__init__(self.message, extra_context=extra_context, **kwargs)
    
    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        if hasattr(self, "resource_type"):
            result["resource_type"] = self.resource_type
        if hasattr(self, "resource_id"):
            result["resource_id"] = str(self.resource_id)

# Focused errors

class EmotionalEventIngestionError(BaseDomainError):
    """Failed to ingest emotional events"""

    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        pass
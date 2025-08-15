import structlog
import traceback
import re
from typing import Any, Callable, TypeVar, TYPE_CHECKING
from abc import ABC, abstractmethod

from fastapi import Request, status
from fastapi.responses import JSONResponse

from ecs.core.config import settings

if TYPE_CHECKING:
    from ecs.repositories import BaseDomainError
    from ecs.services import BaseServiceError
    from ecs.api import BaseHandlerError

# Type variable for error types
T = TypeVar('T', bound='BaseError')

class BaseError(Exception, ABC):
    """Base exception class for all application errors"""
    
    def __init__(
        self,
        message: str,
        *,
        extra_context: dict[str, Any] | None = None,
        original_error: Exception | None = None,
        error_code: str | None = None,
        capture_contextvars: bool = True
    ) -> None:
        self.message = message
        self.original_error = original_error
        self.error_code = error_code or self._get_default_error_code()
        
        # Merge explicit context with structlog contextvars
        self.context = self._build_context(extra_context, capture_contextvars)
        
        super().__init__(self.message)
    
    def _build_context(self, explicit_context: dict[str, Any] | None, capture_contextvars: bool) -> dict[str, Any]:
        """Build the final context by merging explicit context with structlog contextvars"""
        context = {}
        
        # Capture structlog contextvars if enabled
        if capture_contextvars:
            try:
                from structlog.contextvars import get_contextvars
                contextvars_data = get_contextvars()
                if contextvars_data:
                    # Convert UUIDs to strings for JSON serialization
                    context.update(self._serialize_contextvars(contextvars_data))
            except Exception:
                pass
        
        # Merge with explicit context (explicit context takes precedence in case keys conflict)
        if explicit_context:
            context.update(explicit_context)
            
        return context
    
    def _serialize_contextvars(self, contextvars_data: dict[str, Any]) -> dict[str, Any]:
        """Convert contextvars data to JSON-serializable format"""
        serialized = {}
        for key, value in contextvars_data.items():
            if hasattr(value, '__str__'):
                # Convert UUIDs and other objects to strings
                serialized[key] = str(value)
            else:
                serialized[key] = value
        return serialized
    
    def _get_default_error_code(self) -> str:
        """Get default error code based on class name"""
        return self.__class__.__name__.upper()
    
    def __str__(self) -> str:
        return self.message
    
    def to_dict(self, include_details: bool = False) -> dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        result: dict[str, Any] = {
            "error": self._get_error_title(),
            "message": self.message,
            "error_code": self.error_code
        }
        
        # Add subclass-specific fields
        self._add_subclass_fields(result)
        
        if include_details:
            if self.context:
                result["context"] = self.context
            if self.original_error:
                result["original_error"] = str(self.original_error)
                result["original_error_type"] = self.original_error.__class__.__name__
                
        return result
    
    def _get_error_title(self) -> str:
        """Human-readable error title"""
        name = self.__class__.__name__
        name = re.sub(r"(Error|Exception)$", "", name)
        name = name.replace('_', ' ')
        name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        words = [w if w.isupper() else w.capitalize() for w in name.split(" ")]
        return " ".join(words)
    
    @abstractmethod
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        """Add subclass-specific fields to the result dict. Override in subclasses."""
        ...

# Uncaught exceptions are handled here
async def global_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger = structlog.get_logger()
    
    # Always log the full error with traceback for debugging
    logger.error(
        "Unhandled exception",
        exception_type=exc.__class__.__name__,
        exception_message=str(exc),
        traceback=traceback.format_exc(),
    )

    # Determine response content based on environment
    if settings.should_include_error_details:
        # Development: Show detailed error information
        content = {
            "error": "Internal Server Error",
            "message": str(exc),
            "exception_type": exc.__class__.__name__,
            "traceback": traceback.format_exc().split('\n')[-5:],  # Last 5 lines
        }
    else:
        # Production: Generic error message
        content = {
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content
    )

async def application_error_handler(layer: str, status_code_mapper_func: Callable[[T], int], request: Request, exc: T) -> JSONResponse:
    """Generic handler for all application errors"""
    logger = structlog.get_logger()
    
    # Log with context (contextvars are automatically included via structlog)
    logger.error(
        f"{layer} error",
        exception_type=exc.__class__.__name__,
        message=exc.message,
        error_code=exc.error_code,
        context=exc.context,
        original_error=str(exc.original_error) if exc.original_error else None
    )

    # Use the exception's to_dict method for consistent formatting
    content = exc.to_dict(include_details=settings.should_include_error_details)
    
    # Map exception types to appropriate HTTP status codes
    status_code = status_code_mapper_func(exc)
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )

async def domain_error_handler(request: Request, exc: "BaseDomainError") -> JSONResponse:
    return await application_error_handler(
        "Domain", _get_status_code_for_domain_exception, request, exc)

async def service_error_handler(request: Request, exc: "BaseServiceError") -> JSONResponse:
    return await application_error_handler(
        "Service", _get_status_code_for_service_exception, request, exc)

async def handler_error_handler(request: Request, exc: "BaseHandlerError") -> JSONResponse:
    return await application_error_handler(
        "Handler", _get_status_code_for_handler_exception, request, exc)

def _get_status_code_for_domain_exception(exc: "BaseDomainError") -> int:
    """Map domain exception types to HTTP status codes"""
    from ecs.repositories import NotFoundError

    if isinstance(exc, NotFoundError):
        return status.HTTP_404_NOT_FOUND
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR

def _get_status_code_for_service_exception(exc: "BaseServiceError") -> int:
    """Map service exception types to HTTP status codes"""
    from ecs.services import BusinessLogicError, UnauthorizedError, ForbiddenError

    if isinstance(exc, BusinessLogicError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, UnauthorizedError):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ForbiddenError):
        return status.HTTP_403_FORBIDDEN
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR

def _get_status_code_for_handler_exception(exc: "BaseHandlerError") -> int:
    """Map handler exception types to HTTP status codes"""
    if exc.status_code:
        return exc.status_code
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
from typing import override, Any

from fastapi import status
from ecs.core.exceptions import BaseError

class BaseHandlerError(BaseError):
    """Base exception class for all service errors"""
    def __init__(self, status_code: int, *args, **kwargs) -> None:
        self.status_code = status_code
        super().__init__(*args, **kwargs)

class BadRequestError(BaseHandlerError):
    """Application level bad request error"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, *args, **kwargs)
    
    @override
    def _add_subclass_fields(self, result: dict[str, Any]) -> None:
        result["status_code"] = self.status_code
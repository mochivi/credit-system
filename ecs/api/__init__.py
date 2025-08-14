from fastapi import APIRouter

from ecs.api.routes import v1router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1router)

from ecs.api.exceptions import BaseHandlerError, BadRequestError
from ecs.api.middleware import RequestLogMiddleware

__all__ = [
    "api_router",
    
    "RequestLogMiddleware",

    "BaseHandlerError",
    "BadRequestError",
]
from fastapi import APIRouter

from ecs.api.routes.v1 import health_router

v1router = APIRouter(prefix="/v1")
v1router.include_router(health_router)
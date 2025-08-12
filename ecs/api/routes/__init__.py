from fastapi import APIRouter

from ecs.api.routes.v1 import health_router, login_router, credit_router, emotions_router

v1router = APIRouter(prefix="/v1")
v1router.include_router(health_router)
v1router.include_router(login_router)
v1router.include_router(credit_router)
v1router.include_router(emotions_router)
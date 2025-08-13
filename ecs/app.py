from typing import AsyncGenerator

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute

from ecs.core.config import settings
from ecs.core.logging import configure_logging
from ecs.core.db import SessionLocal, init_db
from ecs.core.exceptions import global_exception_handler
from ecs.api import api_router
from ecs.api.middleware import RequestLogMiddleware

def generate_custom_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

def setup_app(app: FastAPI):
    # Register routes
    app.include_router(api_router)

    # Add middlewares - first is innermost, last is outermost
    app.add_middleware(RequestLogMiddleware)

    # Global exception handler
    app.add_exception_handler(Exception, global_exception_handler)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with SessionLocal() as session:
        try:
            await init_db(session)
        except:
            await session.close()
    yield

configure_logging()

app = FastAPI(
    title=settings.TITLE,
    lifespan=lifespan,
)
setup_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
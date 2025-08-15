from fastapi import FastAPI
from fastapi.routing import APIRoute

from ecs.core.config import settings
from ecs.core.logging import configure_logging
from ecs.core.exceptions import global_error_handler, domain_error_handler, service_error_handler, handler_error_handler
from ecs.repositories.exceptions import BaseDomainError
from ecs.services.exceptions import BaseServiceError
from ecs.api.exceptions import BaseHandlerError
from ecs.api import api_router, RequestLogMiddleware

def generate_custom_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

def setup_app(app: FastAPI):
    # Register routes
    app.include_router(api_router)

    # Add middlewares - first is innermost, last is outermost
    app.add_middleware(RequestLogMiddleware)

    # Global exception handler
    app.add_exception_handler(Exception, global_error_handler)

configure_logging()

app = FastAPI(
    title=settings.TITLE,
)
setup_app(app)

# Register exception handlers
app.add_exception_handler(BaseDomainError, domain_error_handler) # type: ignore
app.add_exception_handler(BaseServiceError, service_error_handler) # type: ignore
app.add_exception_handler(BaseHandlerError, handler_error_handler) # type: ignore
app.add_exception_handler(Exception, global_error_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
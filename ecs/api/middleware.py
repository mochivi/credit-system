import time, uuid, structlog
from typing import override

from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

class RequestLogMiddleware(BaseHTTPMiddleware):
    
    @override
    async def dispatch(self, request: Request, call_next):
        logger = structlog.get_logger()
        clear_contextvars()
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        bind_contextvars(
            request_id=req_id,
            method=request.method,
            path=request.url.path,
            user_agent=request.headers.get("user-agent", ""),
            client_ip=request.client.host if request.client else "",
        )
        
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.exception("Unhandled exception", duration_ms=duration_ms)
            raise
        
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "Request completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers["X-Request-ID"] = req_id
        return response
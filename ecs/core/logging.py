import logging, structlog
from structlog.processors import JSONRenderer, TimeStamper

from ecs.core.config import settings

def configure_logging():
    log_level: str = settings.LOG_LEVEL.upper()
    logging.basicConfig(level=log_level)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            TimeStamper(fmt="iso"),
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
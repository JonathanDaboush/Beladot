import structlog
import logging
import sys
from fastapi import Request

# Configure structlog for JSON output
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Helper to inject request_id into logs
async def log_request_start(request: Request):
    logger.info(
        "request.start",
        method=request.method,
        path=request.url.path,
        request_id=getattr(request.state, "request_id", None),
        client=request.client.host if request.client else None,
    )

async def log_request_end(request: Request, status_code: int, latency: float):
    logger.info(
        "request.end",
        method=request.method,
        path=request.url.path,
        status_code=status_code,
        latency=latency,
        request_id=getattr(request.state, "request_id", None),
    )

# Usage: import logger, log_request_start, log_request_end

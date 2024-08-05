import logging
import os
import uuid
from typing import Any, Awaitable, Callable, cast

import structlog
from fastapi import Request, Response
from structlog.types import Processor

uvicorn_error = logging.getLogger('uvicorn.error')
uvicorn_error.disabled = True
uvicorn_access = logging.getLogger('uvicorn.access')
uvicorn_access.disabled = True

shared_processors: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt='iso', utc=False),
]

env = os.environ.get('APP_ENV', 'development')
processors: list[Processor] | None = None

if env == 'development':
    processors = shared_processors + [
        structlog.dev.ConsoleRenderer(),
    ]
else:
    processors = shared_processors + [
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]

if processors is not None:
    structlog.configure(
        processors,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a logger instance configured with the project's settings.

    Args:
        name (str): The name of the logger, typically __name__.

    Returns:
        structlog.BoundLogger: A configured structlog logger instance.
    """
    return structlog.get_logger(name)


async def log_request_helper(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """FastAPI Middleware which will handle logging each request."""
    client = request.client
    if client is not None:
        client_host = client.host

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        path=request.url.path,
        method=request.method,
        client_host=cast(Any, client_host),
        request_id=str(uuid.uuid4()),
    )
    response = await call_next(request)

    structlog.contextvars.bind_contextvars(
        status_code=response.status_code,
    )

    log = get_logger('fastapi.middleware.request')

    # Exclude /healthcheck endpoint from producing logs
    if request.url.path != '/healthcheck':
        if 400 <= response.status_code < 500:
            log.warn('Client error')
        elif response.status_code >= 500:
            log.error('Server error')
        else:
            log.info('OK')

    return response

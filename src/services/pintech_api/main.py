from http import HTTPStatus
from typing import Awaitable, Callable, Final
import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from common.logger import log_request_helper

API_DOCS_TITLE = "PinTech API"
API_DOCS_DESC = "PinTech API Documentation"
API_VER: Final[str] = "0.1"

app = FastAPI(
    title=API_DOCS_TITLE,
    description=API_DOCS_DESC,
    version=API_VER,
    docs_url=None,
    redoc_url=None,
)
logger = structlog.get_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logger_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """FastAPI Middleware which will handle logging each request."""
    response = await log_request_helper(request, call_next)
    return response


@app.get(
    "/healthcheck",
    summary="Report the api is running and any other health-check dependencies that need tested.",
    status_code=HTTPStatus.OK,
    include_in_schema=False,
)
async def health_check() -> str:
    """Verify API is running."""
    return "OK"


@app.get(
    "/version",
    summary="Get the current version of the pintech-api",
    status_code=HTTPStatus.OK,
    include_in_schema=False,
)
async def dugong_version() -> str:
    """Running API version."""
    return API_VER


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

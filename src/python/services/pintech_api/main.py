import asyncio
from http import HTTPStatus
from typing import Awaitable, Callable, Final

import structlog
import uvicorn
from common.logger import log_request_helper
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

API_DOCS_TITLE = 'PinTech API'
API_DOCS_DESC = 'PinTech API Documentation'
API_VER: Final[str] = '0.1'
MONGO_URI = 'mongodb://localhost:27017'
MONGO_TIMEOUT = 5  # 5 second timeout

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
    allow_origins=['*'],  # nosemgrep
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def logger_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """FastAPI Middleware which will handle logging each request."""
    response = await log_request_helper(request, call_next)
    return response


@app.get(
    '/healthcheck',
    summary='Report the API and MongoDB status.',
    response_model=dict,
    include_in_schema=False,
)
async def health_check() -> JSONResponse:
    """Verify API is running and check MongoDB connection."""
    status = {'API': 'OK', 'Datastore': 'OK'}
    http_status = HTTPStatus.OK

    # Check MongoDB connection
    client: MongoClient = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIMEOUT * 1000)
    try:
        # Use asyncio.wait_for to set a timeout for the MongoDB operation
        await asyncio.wait_for(asyncio.to_thread(client.admin.command, 'ismaster'), timeout=MONGO_TIMEOUT)
    except (ConnectionFailure, ServerSelectionTimeoutError, asyncio.TimeoutError):
        status['Datastore'] = 'FAILED'
        http_status = HTTPStatus.SERVICE_UNAVAILABLE
    finally:
        client.close()

    return JSONResponse(content=status, status_code=http_status)


@app.get(
    '/version',
    summary='Get the current version of the pintech-api',
    status_code=HTTPStatus.OK,
    include_in_schema=False,
)
async def pintech_api_version() -> dict:
    """Return API version."""
    return {'Version': API_VER}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')

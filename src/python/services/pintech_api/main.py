import asyncio
from http import HTTPStatus
from typing import Awaitable, Callable

import uvicorn
from common.logger import get_logger, log_request_helper
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from services.pintech_api.config import PintechAPISettings

settings: PintechAPISettings = PintechAPISettings.load()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.api_docs_title,
    description=settings.api_docs_desc,
    version=settings.api_ver,
    # docs_url=None,
    # redoc_url=None,
)


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
    client: MongoClient = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=settings.mongo_timeout * 1000)
    try:
        # Use asyncio.wait_for to set a timeout for the MongoDB operation
        await asyncio.wait_for(asyncio.to_thread(client.admin.command, 'ismaster'), timeout=settings.mongo_timeout)
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
    return {'Version': settings.api_ver}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')

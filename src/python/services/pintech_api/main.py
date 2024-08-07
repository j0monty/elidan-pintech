import asyncio
import json
import os
import traceback
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Dict

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from common.logger import get_logger, log_request_helper, setup_logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from services.pintech_api.config import PintechAPISettings

LOG_JSON_FORMAT = TypeAdapter(bool).validate_python(os.getenv('LOG_JSON_FORMAT', False))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
setup_logging(json_logs=LOG_JSON_FORMAT, log_level=LOG_LEVEL)
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


# This middleware must be placed after the logging, to populate the context with the request ID
#
# Answer: middlewares are applied in the reverse order of when they are added (you can verify this
# by debugging `app.middleware_stack` and recursively drilling down the `app` property).
app.add_middleware(CorrelationIdMiddleware)


@app.get(
    '/healthcheck',
    summary='Report the API and MongoDB status.',
    response_model=dict,
    include_in_schema=True,
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
    except (ConnectionFailure, ServerSelectionTimeoutError, asyncio.TimeoutError) as e:
        exception_info: Dict[str, Any] = {
            'exception_type': type(e).__name__,
            'exception_message': str(e),
            'mongo_uri': settings.mongo_uri,  # Be careful not to log sensitive information
            'mongo_timeout': settings.mongo_timeout,
            'traceback': traceback.format_exc(),
        }
        logger.error('MongoDB connection failed', extra=exception_info)
        status['Datastore'] = 'FAILED'
        http_status = HTTPStatus.SERVICE_UNAVAILABLE
    finally:
        client.close()

    return JSONResponse(content=status, status_code=http_status)


@app.get(
    '/version',
    summary='Get the current version of the pintech-api',
    status_code=HTTPStatus.OK,
    include_in_schema=True,
)
async def pintech_api_version() -> dict:
    """Return API version."""
    return {'Version': settings.api_ver}


def load_log_config(config_path: str) -> Dict[str, Any]:
    """
    Load and parse a JSON configuration file.

    Args:
        config_path (str): The path to the JSON configuration file.

    Returns:
        Dict[str, Any]: A dictionary containing the parsed JSON configuration.

    Raises:
        JSONDecodeError: If the file contains invalid JSON.
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the user doesn't have permission to read the file.
    """
    with open(config_path) as config_file:
        config = json.load(config_file)
    return config


if __name__ == '__main__':
    # NOTE: the log_config disabled all uvicorn logging, so if there's an issue in the underlying logging system no
    # errors will be emitted.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_config = load_log_config(os.path.join(current_dir, 'uvicorn_disable_logging.json'))

    uvicorn.run(app, host='127.0.0.1', port=8000, server_header=False, log_level='debug', log_config=log_config)

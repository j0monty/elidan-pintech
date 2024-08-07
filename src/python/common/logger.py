import logging
import sys
import time
from types import TracebackType
from typing import Any, Awaitable, Callable, Dict, Optional, Type, cast

import structlog
from asgi_correlation_id.context import correlation_id
from fastapi import Request, Response
from structlog.types import EventDict, Processor
from uvicorn._types import WWWScope
from uvicorn.protocols.utils import get_path_with_query_string


def drop_color_message_key(_: Any, __: Any, event_dict: EventDict) -> EventDict:
    """
    Remove the 'color_message' key from the event dictionary.

    This function is a structlog processor that removes the redundant 'color_message'
    key added by Uvicorn from the log event dictionary. Uvicorn logs the message a
    second time in this key, which is not needed for our logging setup.

    Args:
        _ (Any): Placeholder for logger (unused).
        __ (Any): Placeholder for method name (unused).
        event_dict (EventDict): The log event dictionary to be processed.

    Returns:
        EventDict: The processed log event dictionary with 'color_message' removed.

    Note:
        This function is designed to be used as a processor in a structlog
        processing chain. It modifies the event_dict in-place and returns it.
    """
    event_dict.pop('color_message', None)
    return event_dict


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Retrieve a logger instance configured with the project's settings.

    This function returns a structlog logger instance that is set up according
    to the project's logging configuration. It's a wrapper around
    structlog.stdlib.get_logger to ensure consistent logger setup across the project.

    Args:
        name (str, optional): The name of the logger. Defaults to the name of
            the module in which this function is called (__name__).

    Returns:
        structlog.stdlib.BoundLogger: A configured structlog logger instance.

    Note:
        The returned logger is already bound with the module name, which can be
        used for filtering or additional context in log entries.
    """
    return structlog.stdlib.get_logger(name)


async def log_request_helper(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """FastAPI Middleware which will handle logging each request."""
    structlog.contextvars.clear_contextvars()

    # These context vars will be added to all log entries emitted during the request
    request_id = correlation_id.get()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    client = request.client
    if client is not None:
        client_host = client.host
        client_port = client.port

    response = await call_next(request)

    structlog.contextvars.bind_contextvars(
        status_code=response.status_code,
    )

    start_time = time.perf_counter_ns()
    # If the call_next raises an error, we still want to return our own 500 response,
    # so we can add headers to it (process time, request ID...)
    response = Response(status_code=500)

    try:
        response = await call_next(request)
    except Exception:
        # TODO: Validate that we don't swallow exceptions (unit test?)
        structlog.stdlib.get_logger('api.error').exception('Uncaught exception')
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code
        if request.scope['type'] in ('http', 'websocket'):
            url: str = get_path_with_query_string(cast(WWWScope, request.scope))
        else:
            url = 'Unknown request scope.'

        client_host = client_host
        client_port = client_port
        http_method = request.method
        http_version = request.scope['http_version']
        # Recreate the Uvicorn access log format, but add all parameters as structured information
        get_logger().info(
            f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
            http={
                'url': str(request.url),
                'status_code': status_code,
                'method': http_method,
                'request_id': request_id,
                'version': http_version,
            },
            network={'client': {'ip': client_host, 'port': client_port}},
            duration=process_time,
        )
        response.headers['X-Process-Time'] = str(process_time / 10**9)
    # Exclude /healthcheck endpoint from producing logs
    # if request.url.path != '/healthcheck':
    #    if 400 <= response.status_code < 500:
    #        log.warn('Client error')
    #    elif response.status_code >= 500:
    #        log.error('Server error')
    #    else:
    #        log.info('OK')

    return response


def setup_logging(json_logs: bool = False, log_level: str = 'INFO') -> None:
    """
    Configure structured logging for the application.

    This function sets up logging using structlog, configuring it for use with
    uvicorn/fastapi. It adds a correlation ID and supports both JSON and console logging.

    Args:
        json_logs (bool, optional): Whether to output logs in JSON format.
            Defaults to False.
        log_level (str, optional): The log level to use. Defaults to "INFO".

    Returns:
        None

    Note:
        This function configures global logging settings and does not return anything.
        It sets up shared processors for all log entries and configures different
        renderers based on whether JSON logging is enabled.
    """
    timestamper = structlog.processors.TimeStamper(fmt='iso')

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # Add extra attributes of LogRecord objects to the event dictionary
        # so that values passed in the extra parameter of log methods pass
        # through to log output.
        structlog.stdlib.ExtraAdder(),
        drop_color_message_key,
        timestamper,
    ]

    if json_logs:
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors
        + [
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor
    if json_logs:
        log_renderer = structlog.processors.JSONRenderer()
    else:
        log_renderer = structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    for _log in ['uvicorn', 'uvicorn.error']:
        # Clear the log handlers for uvicorn loggers, and enable propagation
        # so the messages are caught by our root logger and formatted correctly
        # by structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    # Since we re-create the access logs ourselves, to add all information
    # in the structured log (see the `logging_middleware` in main.py), we clear
    # the handlers and prevent the logs to propagate to a logger higher up in the
    # hierarchy (effectively rendering them silent).
    logging.getLogger('uvicorn.access').handlers.clear()
    logging.getLogger('uvicorn.access').propagate = False

    def handle_exception(
        exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Optional[TracebackType]
    ) -> Any:
        """
        Log uncaught exceptions while allowing KeyboardInterrupt to pass through.

        This function serves as a custom exception handler, logging all uncaught
        exceptions except for KeyboardInterrupt. It's designed to be used as a
        sys.excepthook replacement.

        Args:
            exc_type (Type[BaseException]): The type of the exception.
            exc_value (BaseException): The exception instance.
            exc_traceback (Optional[TracebackType]): A traceback object encapsulating the call stack, or None.

        Returns:
            Any: This function doesn't return anything meaningful, but the return type is Any to match sys.excepthook.

        Note:
            This function logs the exception using the root logger at the ERROR level.
            For KeyboardInterrupt, it calls the original sys.__excepthook__ to maintain
            normal Ctrl+C functionality.

        Reference:
            Inspired by https://stackoverflow.com/a/16993115/3641865
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error('Uncaught exception', exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def get_log_config(log_level: str) -> Dict[str, Any]:
    """
    Generate a logging configuration dictionary for Uvicorn.

    This function creates a logging configuration based on the provided log level.
    The configuration includes settings for the default logger and the access logger.

    Args:
        log_level (str): The desired log level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
                         Should be provided in uppercase.

    Returns:
        Dict[str, Any]: A dictionary containing the logging configuration with the following structure:
            {
                "version": int,
                "disable_existing_loggers": bool,
                "formatters": Dict[str, Dict[str, Any]],
                "handlers": Dict[str, Dict[str, Any]],
                "loggers": Dict[str, Dict[str, Any]]
            }

    Example:
        >>> config = get_log_config("DEBUG")
        >>> config['loggers']['uvicorn']['level']
        'DEBUG'

    Note:
        This function is designed to work with Uvicorn's logging system. The returned
        configuration can be passed directly to uvicorn.run()'s log_config parameter.
    """
    json_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'access': {
                '()': 'uvicorn.logging.AccessFormatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'default': {
                '()': 'uvicorn.logging.DefaultFormatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'access': {'class': 'logging.NullHandler', 'formatter': 'access'},
            'default': {'class': 'logging.NullHandler', 'formatter': 'default'},
        },
        'loggers': {
            'uvicorn.access': {'handlers': ['access'], 'level': log_level, 'propagate': False},
            'uvicorn.error': {'handlers': ['default'], 'level': log_level, 'propagate': False},
        },
    }
    return json_config

import asyncio
import os
from typing import Any
from typing import Callable
from typing import Iterable

import structlog
import structlog_gcp
from structlog import stdlib
from structlog.dev import ConsoleRenderer
from structlog.processors import KeyValueRenderer
from structlog.processors import StackInfoRenderer
from structlog.processors import TimeStamper
from structlog.processors import UnicodeDecoder
from structlog.processors import format_exc_info
from structlog.typing import EventDict
from structlog.typing import Processor
from structlog.typing import WrappedLogger


def format_kwargs(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    try:
        msg = event_dict["event"].format(**event_dict)
    except KeyError:
        # This happens if the original event message contains formatting
        # markers, which are not formatting markers.
        # For example: `Fetching Pub/Sub topic for: {'@type':
        # 'type.googleapis.com/google.pubsub.v1.PubsubMessage',
        # 'attributes': {}}`
        # In this case, silently ignore the error and log the message as it
        # is.
        msg = event_dict["event"]

    event_dict["event"] = msg
    return event_dict


def configure(*, format: str | None = "gcp") -> None:
    if format is None:
        format = os.getenv("LOG_FORMAT")

    processors: list[Processor] = [
        # format the log message from the keyword arguments
        format_kwargs,
    ]

    if format == "gcp":
        processors.extend(structlog_gcp.build_processors())
    else:
        if format != "test":
            # Add a timestamp in ISO 8601 format.
            processors.append(TimeStamper(fmt="iso"))

        procs: Iterable[Callable[[Any, Any, Any], Any]] = [
            # Add log level to event dict.
            stdlib.add_log_level,
            # Perform %-style formatting.
            stdlib.PositionalArgumentsFormatter(),
            # If the "stack_info" key in the event dict is true, remove it and
            # render the current stack trace in the "stack" key.
            StackInfoRenderer(),
            # If the "exc_info" key in the event dict is either true or a
            # sys.exc_info() tuple, remove "exc_info" and render the exception
            # with traceback into the "exception" key.
            format_exc_info,
            # If some value is in bytes, decode it to a unicode str.
            UnicodeDecoder(),
        ]
        processors.extend(procs)

        if format == "test":
            processors.append(KeyValueRenderer())
        else:
            processors.append(ConsoleRenderer())

    structlog.configure(processors=processors, cache_logger_on_first_use=True)


def loop_error_handler_installer() -> None:
    """Configure the asyncio loop error handler.

    See: https://docs.python.org/3/library/asyncio-eventloop.html#error-handling-api

    This should be called from within a coroutine, while a loop is running.
    """

    def asyncio_exception_handler(
        loop: asyncio.AbstractEventLoop, context: dict[str, Any]
    ) -> None:
        """Log the uncaught exceptions from asyncio"""

        logger = structlog.get_logger("asyncio")
        message = context.pop("message")
        logger.exception(message, **context)

    loop = asyncio.get_running_loop()
    loop.set_exception_handler(asyncio_exception_handler)

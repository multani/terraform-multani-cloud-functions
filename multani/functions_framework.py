"""Functions framework helpers

This provides alternative features on top of the upstream functions-framework project.

See:

* https://cloud.google.com/functions/docs/functions-framework
* https://github.com/GoogleCloudPlatform/functions-framework-python
"""

import functools

import functions_framework
import structlog
from cloudevents.http.event import CloudEvent
from flask import Request
from flask.typing import ResponseReturnValue
from functions_framework import CloudEventFunction
from functions_framework import HTTPFunction


def cloud_event(func: CloudEventFunction) -> CloudEventFunction:
    """Helper to wrap a Cloud Event and log the result into a structlog logger.

    The logger should report errors to Google Error Reporting system, if the
    Cloud Function handler fails.
    """

    @functools.wraps(func)
    def logging_handler(event: CloudEvent) -> None:
        """Call the Cloud Function and log errors."""

        logger = structlog.get_logger()

        try:
            result = func(event)
        except Exception as exc:
            logger.exception(f"Error calling {func}", exception=exc)
            return

        return result

    return functions_framework.cloud_event(logging_handler)


def http(func: HTTPFunction) -> HTTPFunction:
    @functools.wraps(func)
    def logging_handler(request: Request) -> ResponseReturnValue:
        """Call the Cloud Function and log errors."""

        logger = structlog.get_logger()

        try:
            result = func(request)
        except Exception as exc:
            logger.exception(f"Error calling {func}", exception=exc)
            return ("Error", 500)

        return result

    return functions_framework.http(logging_handler)

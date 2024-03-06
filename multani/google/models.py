from typing import Self

import flask
import structlog
from pydantic import BaseModel

LOGGER = structlog.get_logger()


class ErrorReportingGroupInfo(BaseModel):
    project_id: str
    detail_link: str


class ErrorReportingExceptionInfo(BaseModel):
    type: str
    message: str


class ErrorReportingEventInfo(BaseModel):
    log_message: str
    request_method: str
    request_url: str
    referrer: str
    user_agent: str
    service: str
    version: str
    response_status: str


class ErrorReporting(BaseModel):
    version: str
    subject: str
    group_info: ErrorReportingGroupInfo
    exception_info: ErrorReportingExceptionInfo
    event_info: ErrorReportingEventInfo

    @classmethod
    def from_request(cls, request: flask.Request) -> Self:
        content_type = request.headers.get("content-type")
        if content_type != "application/json":
            raise ValueError(f"Invalid request content type: {content_type}")

        try:
            data = request.json
        except:  # noqa: E722
            LOGGER.exception("Unable to parse JSON content", payload=request.data)
            raise ValueError("JSON content-type, but not able to parse JSON payload")

        LOGGER.debug("Received an error", error=data)

        return cls.model_validate(data)


def is_test_notification(request: flask.Request) -> bool:
    """Is the notification received in the request a "test" notification?

    A "test" notification is sent when the webhook is being tested by GCP.

    In this case, the webhook receives a payload where the content if an
    Incident object and the `version` field is set to "test".

    Anything is *not* considered a test notification.
    """

    try:
        return request.json is not None and request.json.get("version") == "test"
    except:  # noqa: E722
        return False

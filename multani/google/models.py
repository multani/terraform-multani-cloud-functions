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

        LOGGER.debug("Received an error", error=request.json)

        return cls.model_validate_json(request.data)

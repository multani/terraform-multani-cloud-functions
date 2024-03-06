import os.path
from pathlib import Path

import pytest
from flask import Request
from pydantic import ValidationError
from werkzeug.test import EnvironBuilder

from multani.google.models import ErrorReporting
from multani.google.models import is_test_notification

FIXTURES = Path(os.path.abspath(__file__)).parent / "fixtures"


def new_request(payload: str) -> Request:
    wsgi_env = EnvironBuilder(
        headers=[("content-type", "application/json")],
        data=payload,
    )
    request = Request(wsgi_env.get_environ())
    return request


def test_parse_test_notification() -> None:
    payload = FIXTURES / "error-reporting" / "test-notification-1.json"
    request = new_request(payload.read_text())

    with pytest.raises(ValidationError):
        ErrorReporting.from_request(request)

    assert is_test_notification(request)


def test_parse_error_1() -> None:
    payload = FIXTURES / "error-reporting" / "error-1.json"
    request = new_request(payload.read_text())

    e = ErrorReporting.from_request(request)
    assert e.version == "1.0"


def test_parse_error_broken_json() -> None:
    # This JSON fixture contains a broken JSON escape sequence "\'", that was
    # serialized by GCP...
    payload = r"""
    {
      "version": "1.0",
      "subject": "New error in multani-admin terraform-cloud-trigger terraform-cloud-trigger-00002-tih",
      "group_info" : {
        "project_id": "multani-admin",
        "detail_link": "https://console.cloud.google.com/errors/CJ_1w4ilk-PGcA?project=multani-admin&time=P30D&utm_source=error-reporting-notification&utm_medium=webhook&utm_content=new-error"
      },
      "exception_info" : {
        "type": "KeyError",
        "message": "data"
      },
      "event_info": {
        "log_message": "Error calling <function terraform_cloud_trigger_all at 0x3ed48f0c98a0>\nTraceback (most recent call last):\n  File \"/workspace/multani/functions_framework.py\", line 36, in logging_handler\n    result = func(event)\n             ^^^^^^^^^^^\n  File \"/workspace/multani/functions.py\", line 33, in terraform_cloud_trigger_all\n    data = json.loads(urlsafe_b64decode(event[\"data\"]).decode(\"utf-8\"))\n                                        ~~~~~^^^^^^^^\n  File \"/layers/google.python.pip/pip/lib/python3.12/site-packages/cloudevents/abstract/event.py\", line 105, in __getitem__\n    return self._get_attributes()[key]\n           ~~~~~~~~~~~~~~~~~~~~~~^^^^^\nKeyError: \'data\'",
        "request_method": "",
        "request_url": "",
        "referrer": "",
        "user_agent": "",
        "service": "terraform-cloud-trigger",
        "version": "terraform-cloud-trigger-00002-tih",
        "response_status": "0"
      }
    }
    """
    request = new_request(payload)

    e = ErrorReporting.from_request(request)
    assert e.version == "1.0"

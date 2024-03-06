from pydantic import ValidationError
import pytest
import os.path
from pathlib import Path

from flask import Request
from werkzeug.test import EnvironBuilder

from multani.google.models import ErrorReporting, is_test_notification

FIXTURES = Path(os.path.abspath(__file__)).parent / "fixtures"


def test_parse_test_notification() -> None:
    payload = FIXTURES / "error-reporting" / "test-notification-1.json"

    wsgi_env = EnvironBuilder(
        headers=[("content-type", "application/json")],
        data=payload.read_text(),
    )
    request = Request(wsgi_env.get_environ())

    with pytest.raises(ValidationError):
        ErrorReporting.from_request(request)

    assert is_test_notification(request)

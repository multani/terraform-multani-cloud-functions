from typing import Generator

import pytest
from flask import Flask
from flask import request
from flask.testing import FlaskClient

from multani import http


@pytest.fixture()
def fake_app() -> Generator[Flask, None, None]:

    app = Flask("test")

    @app.route("/")
    def hello_world() -> str:
        http.check_authorization(request, "username", "password")
        return "OK"

    app.config

    yield app


@pytest.fixture()
def client(fake_app: Flask) -> FlaskClient:
    return fake_app.test_client()


def test_http_auth_ok(client: FlaskClient) -> None:
    r = client.get("/", auth=("username", "password"))

    assert r.status == "200 OK"


def test_http_auth_fail(client: FlaskClient) -> None:
    r = client.get("/", auth=("username", "wrong-password"))
    assert r.status == "401 UNAUTHORIZED"
    assert r.text == "Unauthorized"

    r = client.get("/", auth=("wrong-user", "wrong"))
    assert r.status == "401 UNAUTHORIZED"
    assert r.text == "Unauthorized"

    r = client.get("/")
    assert r.status == "401 UNAUTHORIZED"
    assert r.text == "Unauthorized"

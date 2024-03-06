import httpx
from flask import Request
from flask import Response
from flask import abort


def check_status_json(response: httpx.Response) -> None:
    if response.status_code > 399:
        try:
            error = response.json()
        except:  # noqa: E722
            error = response.text

        request = response.request
        message = f"{response.status_code} for {request.url}: {error}"

        raise httpx.HTTPStatusError(message, request=request, response=response)


def check_authorization(request: Request, username: str, password: str) -> None:
    """Verify the HTTP request satisfy the authentication credentials."""

    unauthorized = Response(
        "Unauthorized",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )

    auth = request.authorization
    if not auth:
        abort(unauthorized)

    if auth.username != username or auth.password != password:
        abort(unauthorized)

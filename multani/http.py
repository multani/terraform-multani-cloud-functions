import httpx


def check_status_json(response: httpx.Response) -> None:
    if response.status_code > 399:
        try:
            error = response.json()
        except:  # noqa: E722
            error = response.text

        request = response.request
        message = f"{response.status_code} for {request.url}: {error}"

        raise httpx.HTTPStatusError(message, request=request, response=response)

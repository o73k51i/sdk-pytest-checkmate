"""Enhanced HTTP client with automatic request/response logging."""

import json

from httpx import URL, Auth, Client, Response

from ._constants import DEFAULT_TIMEOUT
from ._core import add_data_report
from ._types import AnyType, JsonData

__all__ = ["create_http_client"]


def _try_parse_json(data: bytes | str | None) -> JsonData:
    """Attempt to parse data as JSON, returning original data if parsing fails.

    Args:
        data: The data to parse as JSON.

    Returns:
        Parsed JSON data or original data if parsing fails.
    """
    if data is None or data == b"" or data == "":
        return None

    try:
        data_str = data.decode("utf-8") if isinstance(data, bytes) else str(data)
        return json.loads(data_str)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return str(data)


def _format_response_time(elapsed_seconds: float) -> str:
    """Format response time for display.

    Args:
        elapsed_seconds: Response time in seconds.

    Returns:
        Formatted response time string.
    """
    milliseconds = elapsed_seconds * 1000
    return f"{milliseconds:.3f} ms"


def _create_request_log(response: Response) -> dict[str, AnyType]:
    """Create a structured log entry for an HTTP request/response pair.

    Args:
        response: The HTTP response object.

    Returns:
        A dictionary containing request and response information.
    """
    return {
        "method": response.request.method,
        "url": str(response.url),
        "request_headers": dict(response.request.headers),
        "request_body": _try_parse_json(response.request.content),
        "status_code": response.status_code,
        "response_time": _format_response_time(response.elapsed.total_seconds()),
        "response_headers": dict(response.headers),
        "response_body": _try_parse_json(response.content),
    }


class CheckmateHttpClient(Client):
    """Enhanced HTTP client that automatically logs requests and responses.

    This client extends httpx.Client to provide automatic logging of all
    HTTP requests and responses to the test report timeline.
    """

    def request(self, method: str, url: URL | str, **kwargs: AnyType) -> Response:
        """Execute an HTTP request and log the details.

        Args:
            method: HTTP method (GET, POST, etc.).
            url: Request URL.
            **kwargs: Keyword arguments passed to the parent request method.

        Returns:
            The HTTP response object.
        """
        response = super().request(method, url, **kwargs)

        log_entry = _create_request_log(response)

        label = f"HTTP request to `{response.request.method} {response.url}` [{response.status_code}]"
        add_data_report(log_entry, label)

        return response


def create_http_client(
    base_url: str,
    headers: dict[str, str] | None = None,
    verify: bool = True,
    timeout: float | int = DEFAULT_TIMEOUT,
    auth: Auth | None = None,
    **kwargs: AnyType,
) -> CheckmateHttpClient:
    """Create an enhanced HTTP client with automatic request/response logging.

    Args:
        base_url: Base URL for all HTTP requests.
        headers: Optional default headers to include with requests.
        verify: Whether to verify SSL certificates (default: True).
        timeout: Request timeout in seconds.
        auth: Authentication handler (optional).
        **kwargs: Additional arguments passed to httpx.Client.

    Returns:
        An enhanced HTTP client that logs all requests/responses.

    Example:
        >>> client = create_http_client("https://api.example.com")
        >>> response = client.get("/users/123")
        >>> # Request/response details are automatically logged
    """
    return CheckmateHttpClient(
        base_url=base_url,
        headers=headers,
        verify=verify,
        timeout=timeout,
        auth=auth,
        **kwargs,
    )

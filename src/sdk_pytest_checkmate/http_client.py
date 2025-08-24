"""HTTP client module for pytest checkmate.

This module provides an enhanced HTTP client built on top of httpx that automatically
captures and reports HTTP request/response data for testing purposes. The client logs
detailed information about each HTTP interaction including request/response headers,
body content, timing, and status codes.

Classes:
    ClientHttpCheckmate: Extended httpx.Client with automatic request/response logging

Functions:
    create_http_client: Factory function to create a configured HTTP client
"""

import json

from httpx import Auth, Client

from .plugin import add_data_report

__all__ = ["create_http_client"]


def try_to_json(data):
    """Safely attempt to parse data as JSON.

    Converts bytes to string if necessary and attempts to parse as JSON.
    Returns the original data if parsing fails or if data is empty.

    Args:
        data: Data to parse as JSON. Can be bytes, string, or None.

    Returns:
        Parsed JSON object/data if successful, original data otherwise, or None if empty.
    """
    if data is None or data == b"" or data == "":
        return None
    try:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)
    except Exception:
        return data


class ClientHttpCheckmate(Client):
    """Enhanced HTTP client with automatic request/response logging.

    Extends httpx.Client to automatically capture and report detailed information
    about HTTP requests and responses for testing purposes. Each request logs
    method, URL, headers, body, status code, response time, and response data.
    """

    def request(self, *args, **kwargs):
        """Execute HTTP request with automatic logging.

        Performs an HTTP request using the parent Client.request method and
        automatically logs comprehensive request/response information including
        headers, body content, timing, and status codes.

        Args:
            *args: Variable arguments passed to httpx.Client.request
            **kwargs: Keyword arguments passed to httpx.Client.request

        Returns:
            httpx.Response: The response object from the HTTP request
        """
        resp = super().request(*args, **kwargs)
        info_resp = {
            "method": resp.request.method,
            "url": str(resp.url),
            "request_headers": dict(resp.request.headers),
            "request_body": try_to_json(resp.request.content),
            "status_code": resp.status_code,
            "response_time": f"{resp.elapsed.total_seconds():.3f} ms",
            "response_headers": dict(resp.headers),
            "response_body": try_to_json(resp.content),
        }
        add_data_report(
            info_resp,
            f"HTTP request to `{resp.request.method} {resp.url}` [{resp.status_code}]",
        )
        return resp


def create_http_client(
    base_url: str,
    headers: dict | None = None,
    verify: bool = True,
    timeout: float | int = 10.0,
    auth: Auth | None = None,
    **kwargs,
) -> ClientHttpCheckmate:
    """Create a configured HTTP client with automatic logging.

    Factory function that creates and configures a ClientHttpCheckmate instance
    with the specified parameters. The client will automatically log all HTTP
    requests and responses for testing and debugging purposes.

    Args:
        base_url (str): The base URL for HTTP requests
        headers (dict | None, optional): Default headers to include with requests.
            Defaults to None.
        verify (bool, optional): Whether to verify SSL certificates. Defaults to True.
        timeout (float | int, optional): Request timeout in seconds. Defaults to 10.0.
        auth (Auth | None, optional): Authentication handler. Defaults to None.
        **kwargs: Additional keyword arguments passed to the httpx.Client constructor

    Returns:
        ClientHttpCheckmate: Configured HTTP client instance with logging capabilities
    """
    return ClientHttpCheckmate(
        base_url=base_url,
        headers=headers,
        verify=verify,
        timeout=timeout,
        auth=auth,
        **kwargs,
    )

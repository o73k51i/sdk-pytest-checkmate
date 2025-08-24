import pytest

from sdk_pytest_checkmate import soft_assert, step
from sdk_pytest_checkmate.http_client import create_http_client


@pytest.fixture(scope="session")
def http_client():
    client = create_http_client("https://httpbin.org")
    yield client
    client.close()


@pytest.mark.epic("HTTP Client")
@pytest.mark.title("HTTP Client Test with step")
def test_http_client_with_step():
    client = create_http_client("https://httpbin.org")
    with step("GET /get request"):
        response = client.get("/get", params={"param1": "value1"})
        soft_assert(response.status_code == 200, "GET request should succeed")
    with step("POST /post request"):
        response = client.post("/post", json={"key": "value"})
        soft_assert(response.status_code == 200, "POST request should succeed")


@pytest.mark.epic("HTTP Client")
@pytest.mark.title("HTTP Client Test")
def test_http_client_simple():
    client = create_http_client("https://httpbin.org")
    response = client.post("/post", json={"key": "value"})
    soft_assert(response.status_code == 200, "POST request should succeed")


@pytest.mark.epic("HTTP Client")
@pytest.mark.title("HTTP Client Test with Fixture")
def test_http_client_fixture(http_client):
    with step("GET /get request"):
        response = http_client.get("/get", params={"param1": "value1"})
        soft_assert(response.status_code == 200, "GET request should succeed")

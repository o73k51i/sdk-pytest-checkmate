"""Pytest plugin for enriched HTML test reporting.

This plugin extends pytest with enhanced reporting capabilities including:

- **Test Steps**: Record named steps with timing using context managers
- **Soft Assertions**: Non-fatal assertions that collect failures without stopping tests
- **Data Attachments**: Attach arbitrary data objects to test timelines
- **HTTP Client Logging**: Automatic capture of HTTP requests/responses with detailed metrics
- **Epic/Story Grouping**: Organize tests with @pytest.mark.epic and @pytest.mark.story
- **Interactive HTML Reports**: Rich reports with filtering, collapsible sections, and inline data

Quick Start:
    Install the plugin and use the main functions in your tests:

    ```python
    from sdk_pytest_checkmate import step, soft_assert, add_data_report, create_http_client

    def test_user_workflow():
        # Create HTTP client with automatic logging
        client = create_http_client("https://api.example.com")

        with step("Setup user data"):
            user = create_test_user()
            add_data_report(user.__dict__, "Test User")

        with step("Login process"):
            login_response = client.post("/login", json={"username": user.username, "password": user.password})
            soft_assert(login_response.status_code == 200, "Login should succeed")

        with step("Verify dashboard"):
            dashboard_response = client.get("/dashboard")
            soft_assert(dashboard_response.status_code == 200, "Dashboard should be accessible")
            add_data_report(dashboard_response.json(), "Dashboard Data")
    ```

    Generate reports:
    ```bash
    pytest --report-html=report.html --report-title="My Test Suite"
    ```

Functions:
    step(name): Context manager for recording test steps with timing
    soft_assert(condition, message=None): Non-fatal assertion that continues test execution
    add_data_report(data, label): Attach arbitrary data to the test timeline
    create_http_client(base_url, **kwargs): Create HTTP client with automatic request/response logging

Markers:
    @pytest.mark.title(name): Set human-friendly test title
    @pytest.mark.epic(name): Group tests under an epic
    @pytest.mark.story(name): Group tests under a story (within an epic)
"""

from .http_client import create_http_client
from .plugin import add_data_report, soft_assert, step

__all__ = [
    "add_data_report",
    "soft_assert",
    "step",
    "create_http_client",
]

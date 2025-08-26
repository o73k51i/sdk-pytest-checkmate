"""Pytest plugin for enriched HTML test reporting.

This plugin extends pytest with enhanced reporting capabilities including:

- **Test Steps**: Record named steps with timing using context managers
- **Soft Assertions**: Non-fatal assertions that collect failures without stopping tests
- **JSON Schema Validation**: Validate JSON data against schemas with soft assertions
- **Data Attachments**: Attach arbitrary data objects to test timelines
- **HTTP Client Logging**: Automatic capture of HTTP requests/responses with detailed metrics
- **Environment Variables**: Automatic loading of .env files for test configuration
- **Epic/Story Grouping**: Organize tests with @pytest.mark.epic and @pytest.mark.story
- **Interactive HTML Reports**: Rich reports with filtering, collapsible sections, and inline data

Quick Start:
    Install the plugin and use the main functions in your tests:

    ```python
    import os
    from sdk_pytest_checkmate import step, soft_assert, add_data_report, create_http_client, soft_validate_json

    def test_user_workflow():
        # Use environment variables for configuration
        api_url = os.environ.get('API_BASE_URL', 'https://api.example.com')
        client = create_http_client(api_url)

        with step("Setup user data"):
            user = create_test_user()
            add_data_report(user.__dict__, "Test User")
            add_data_report({'api_url': api_url}, "Configuration")

        with step("Login process"):
            login_response = client.post("/login", json={"username": user.username, "password": user.password})
            soft_assert(login_response.status_code == 200, "Login should succeed")

        with step("Verify dashboard"):
            dashboard_response = client.get("/dashboard")
            soft_assert(dashboard_response.status_code == 200, "Dashboard should be accessible")
            add_data_report(dashboard_response.json(), "Dashboard Data")
            
            # Validate response against JSON schema
            user_schema = {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string", "format": "email"}
                },
                "required": ["id", "username", "email"]
            }
            soft_validate_json(dashboard_response.json().get("user"), schema=user_schema)

            # Or validate using schema file
            # soft_validate_json(dashboard_response.json(), schema_path="schemas/dashboard.json")
    ```

    Generate reports with environment configuration:
    ```bash
    # Basic report with automatic .env loading
    pytest --report-html=report.html --report-title="My Test Suite"

    # Custom environment file
    pytest --env-file=staging.env --report-html=staging-report.html
    ```

Functions:
    step(name): Context manager for recording test steps with timing
    soft_assert(condition, message=None): Non-fatal assertion that continues test execution
    add_data_report(data, label): Attach arbitrary data to the test timeline
    create_http_client(base_url, **kwargs): Create HTTP client with automatic request/response logging
    soft_validate_json(data, *, schema=None, schema_path=None): Validate JSON data against schema using soft assertion

Command Line Options:
    --env-file=PATH: Load environment variables from .env file (default: .env)
    --report-html=PATH: Generate HTML report (default: report.html)
    --report-title=TITLE: Set custom title for HTML report
    --report-json=PATH: Export results as JSON file

Markers:
    @pytest.mark.title(name): Set human-friendly test title
    @pytest.mark.epic(name): Group tests under an epic
    @pytest.mark.story(name): Group tests under a story (within an epic)
"""

from .http_client import create_http_client
from .json_validator import soft_validate_json
from .plugin import add_data_report, soft_assert, step

__all__ = [
    "add_data_report",
    "soft_assert",
    "step",
    "create_http_client",
    "soft_validate_json",
]

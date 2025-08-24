# sdk-pytest-checkmate

[![PyPI version](https://badge.fury.io/py/sdk-pytest-checkmate.svg)](https://badge.fury.io/py/sdk-pytest-checkmate)
[![Python Support](https://img.shields.io/pypi/pyversions/sdk-pytest-checkmate.svg)](https://pypi.org/project/sdk-pytest-checkmate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pytest plugin for enriched HTML test reporting with support for test steps, soft assertions, and data attachments.

## Features

- 🔄 **Test Steps**: Record named steps with timing using context managers
- 🔍 **Soft Assertions**: Non-fatal assertions that collect failures without stopping tests
- 📊 **Data Attachments**: Attach arbitrary data objects to test timelines
- 🌐 **HTTP Client Logging**: Enhanced HTTP client with automatic request/response capture
- 📋 **Epic/Story Grouping**: Organize tests with `@pytest.mark.epic` and `@pytest.mark.story`
- 📈 **Interactive HTML Reports**: Rich reports with filtering, collapsible sections, and inline data
- ⚡ **Async Support**: Works with both sync and async test functions

## Installation

```bash
pip install sdk-pytest-checkmate
```

The plugin automatically activates when installed - no additional configuration needed.

## Quick Start

```python
from sdk_pytest_checkmate import step, soft_assert, add_data_report, create_http_client
import pytest

@pytest.mark.epic("User Management")
@pytest.mark.story("User Registration")
@pytest.mark.title("Complete user registration flow")
def test_user_registration():
    # Create HTTP client with automatic logging
    client = create_http_client("https://api.example.com")
    
    with step("Prepare test data"):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "secure123"
        }
        add_data_report(user_data, "Registration Data")
    
    with step("Submit registration form"):
        response = client.post("/register", json=user_data)
        soft_assert(response.status_code == 201, "Registration should return 201")
        soft_assert("id" in response.json(), "Response should contain user ID")
    
    with step("Verify user activation"):
        user_response = client.get(f"/users/{response.json()['id']}")
        soft_assert(user_response.status_code == 200, "User should be retrievable")
        user = user_response.json()
        soft_assert(user.get("is_active"), "User should be activated")
        add_data_report(user, "Created User")
    
    # Final critical assertion
    assert user["email"] == user_data["email"], "Email should match"
```

## Generating Reports

Generate an HTML report with your test results:

```bash
# Basic HTML report
pytest --report-html=report.html

# Custom title and JSON export
pytest --report-html=results.html --report-title="My Test Suite" --report-json=results.json

# Run specific tests with reporting
pytest tests/test_integration.py --report-html=integration-report.html
```

## API Reference

### step(name: str)

Context manager for recording test steps with timing information.

```python
# Synchronous usage
with step("Login user"):
    login_response = authenticate(username, password)

# Asynchronous usage  
async with step("Fetch user data"):
    user_data = await api_client.get_user(user_id)
```

**Parameters:**
- `name`: Human-readable step name that appears in the HTML report

### soft_assert(condition: bool, message: str = None) -> bool

Record a non-fatal assertion that doesn't immediately fail the test.

```python
# Basic soft assertion
soft_assert(response.status_code == 200, "API should return 200")

# Multiple soft assertions - test continues even if some fail
soft_assert(user.name is not None, "User should have a name")
soft_assert(user.email.endswith("@company.com"), "Email should be company domain")
soft_assert(len(user.permissions) > 0, "User should have permissions")

# Test will be marked as failed if any soft assertions failed
```

**Parameters:**
- `condition`: Boolean expression to evaluate
- `message`: Optional descriptive message (defaults to "Soft assertion")

**Returns:** The boolean value of `condition`

### create_http_client(base_url: str, **kwargs) -> ClientHttpCheckmate

Create an enhanced HTTP client with automatic request/response logging.

```python
# Basic HTTP client
client = create_http_client("https://api.example.com")

# With custom headers and authentication
client = create_http_client(
    base_url="https://api.example.com",
    headers={"User-Agent": "MyApp/1.0"},
    timeout=30.0,
    verify=True
)

# All HTTP requests are automatically logged
response = client.get("/users/123")
response = client.post("/users", json={"name": "John", "email": "john@example.com"})
```

**Parameters:**
- `base_url`: Base URL for all HTTP requests
- `headers`: Optional default headers to include with requests
- `verify`: Whether to verify SSL certificates (default: True)
- `timeout`: Request timeout in seconds (default: 10.0)
- `auth`: Authentication handler (optional)
- `**kwargs`: Additional arguments passed to httpx.Client

**Returns:** Enhanced HTTP client that automatically logs all requests/responses to the test report

The client logs comprehensive information for each request:
- Request method, URL, headers, and body
- Response status code, headers, and body
- Response time in milliseconds
- All data is automatically attached to the test timeline

### add_data_report(data: Any, label: str) -> DataRecord

Attach arbitrary data to the test timeline for inspection in HTML reports.

```python
# Attach configuration
config = {"endpoint": "/api/users", "timeout": 30}
add_data_report(config, "API Config")

# Attach response data
add_data_report({
    "status_code": response.status_code,
    "headers": dict(response.headers),
    "body": response.json()
}, "API Response")

# Attach custom objects
add_data_report(user_profile.__dict__, "User Profile")
```

**Parameters:**
- `data`: Any Python object (dict/list will be pretty-printed as JSON)
- `label`: Short label shown in the report UI

## Markers

### @pytest.mark.title(name)

Set a human-friendly test title that appears in reports instead of the function name.

```python
@pytest.mark.title("User can successfully log in with valid credentials")
def test_login_valid_user():
    pass
```

### @pytest.mark.epic(name)

Group tests under an epic for better organization in reports.

```python
@pytest.mark.epic("User Authentication")
def test_login():
    pass

@pytest.mark.epic("User Authentication") 
def test_logout():
    pass
```

### @pytest.mark.story(name)

Group tests under a story (nested under epics) for hierarchical organization.

```python
@pytest.mark.epic("E-commerce")
@pytest.mark.story("Shopping Cart")
def test_add_item_to_cart():
    pass

@pytest.mark.epic("E-commerce")
@pytest.mark.story("Shopping Cart")
def test_remove_item_from_cart():
    pass
```

## Command Line Options

- `--report-html[=PATH]`: Generate HTML report (default: `report.html`)
- `--report-title=TITLE`: Set custom title for HTML report (default: "Pytest report")
- `--report-json=PATH`: Export results as JSON file

## HTML Report Features

The generated HTML reports include:

- **Interactive Filtering**: Filter tests by status (PASSED, FAILED, SKIPPED, etc.)
- **Collapsible Sections**: Expand/collapse epic and story groups
- **Timeline View**: See steps, soft assertions, and data in chronological order
- **Data Inspection**: Click to expand attached data objects
- **Error Details**: Full tracebacks and soft assertion summaries
- **Performance Metrics**: Step timing and total test duration

## Requirements

- Python 3.10+
- pytest 8.4.1+

## License

MIT License - see [LICENSE](LICENSE) file for details.

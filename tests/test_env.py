from os import getenv

import pytest

from sdk_pytest_checkmate import add_data_report


@pytest.mark.epic("ENV variables")
@pytest.mark.title("Test environment variables")
def test_env_variables():
    var = getenv("TEST_VAR")
    add_data_report({"TEST_VAR": var}, "Environment Variables")
    add_data_report(var, "TEST_VAR Value")

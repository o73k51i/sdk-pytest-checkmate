import pytest

from sdk_pytest_checkmate import add_data_report


@pytest.mark.epic("Data in Report")
@pytest.mark.title("Add data to report test")
def test_add_data_to_report():
    add_data_report("Simple text", "String data")
    add_data_report(12345, "Integer data")
    add_data_report(3.14159, "Float data")
    add_data_report({"key": "value", "number": 42}, "Dictionary data")
    add_data_report([1, 2, 3, 4, 5], "List data")
    add_data_report((10, 20, 30), "Tuple data")
    add_data_report({1, 2, 3}, "Set data")
    add_data_report(None, "None data")
    add_data_report(True, "Boolean data")
    add_data_report(b"byte data", "Bytes data")
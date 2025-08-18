"""Pytest plugin for enriched HTML test reporting.

step(name): timeline step context manager (sync/async).

soft_assert(condition, message=None): soft assertion collected for later failure.

add_data_report(data, label): attach arbitrary data to the test timeline.
"""

from .plugin import add_data_report, soft_assert, step

__all__ = [
    "add_data_report",
    "soft_assert",
    "step",
]

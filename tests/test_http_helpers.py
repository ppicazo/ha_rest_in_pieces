"""Unit tests that do not need a running Home Assistant instance."""

from custom_components.rest_in_pieces.const import API_PATH_PREFIX
from custom_components.rest_in_pieces.http import endpoint_path


def test_endpoint_path() -> None:
    assert endpoint_path("abc123") == f"{API_PATH_PREFIX}/abc123"

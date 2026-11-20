import pytest

from api_config import get_service_url


@pytest.mark.parametrize(
    "service, expected_url",
    [
        ("example", "https://example.com"),
        ("github", "https://github.com"),
        ("unknown", None),
    ]
)
def test_get_service_url(service, expected_url):
    """Verify approved service URL lookup."""

    result = get_service_url(service)

    assert result == expected_url

"""Configuration for approved API monitoring targets."""

APPROVED_SERVICES = {
    "example": "https://example.com",
    "github": "https://github.com",
}


def get_service_url(service_name: str) -> str | None:
    """Return the URL for an approved service."""

    return APPROVED_SERVICES.get(service_name)

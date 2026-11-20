import httpx
import server
import pytest


def test_check_api_health_timeout(monkeypatch):
    """Verify that API timeouts are handled correctly."""

    # Simulate an HTTP request that times out
    def mock_get(*args, **kwargs):
        raise httpx.ConnectTimeout("Connection timed out")

    # Replace httpx.get with our mock function
    monkeypatch.setattr(server.httpx, "get", mock_get)

    # Execute the health check
    result = server.check_api_health()

    # Verify the error response
    assert result["status"] == "error"
    assert result["service"] == "example"
    assert result["healthy"] is False
    assert result["error_type"] == "timeout"
    assert result["message"] == "API request timed out"

    # Verify that elapsed time is included
    assert isinstance(result["response_time_ms"], float)
    assert result["response_time_ms"] >= 0


def test_check_api_health_connection_error(monkeypatch):
    """Verify that API connection failures are handled."""

    # Simulate a failed HTTP connection
    def mock_get(*args, **kwargs):
        raise httpx.ConnectError("Connection refused")

    # Replace the real HTTP request with our mock
    monkeypatch.setattr(server.httpx, "get", mock_get)

    # Execute the health check
    result = server.check_api_health()

    # Verify the error response
    assert result["status"] == "error"
    assert result["service"] == "example"
    assert result["healthy"] is False
    assert result["error_type"] == "connection_error"
    assert result["message"] == "Unable to connect to API"

    # Verify elapsed time is included
    assert isinstance(result["response_time_ms"], float)
    assert result["response_time_ms"] >= 0


def test_check_api_health_http_500(monkeypatch):
    """Verify that HTTP 500 responses are marked unhealthy."""

    # Simulate an HTTP 500 response
    def mock_get(*args, **kwargs):
        return httpx.Response(
            status_code=500,
            request=httpx.Request("GET", "https://example.com")
        )

    # Replace the real HTTP request
    monkeypatch.setattr(server.httpx, "get", mock_get)

    # Execute the health check
    result = server.check_api_health()

    # Verify the response
    assert result["status"] == "success"
    assert result["service"] == "example"
    assert result["http_status"] == 500
    assert result["healthy"] is False

    # Verify response time is recorded
    assert isinstance(result["response_time_ms"], float)
    assert result["response_time_ms"] >= 0


@pytest.mark.parametrize(
    "status_code, expected_healthy",
    [
        (200, True),
        (201, True),
        (404, False),
        (500, False),
        (503, False),
    ]
)
def test_check_api_health_status_codes(
    monkeypatch, status_code, expected_healthy
):
    """Verify API health classification for different HTTP codes."""

    # Simulate the selected HTTP response
    def mock_get(*args, **kwargs):
        return httpx.Response(
            status_code=status_code,
            request=httpx.Request("GET", "https://example.com")
        )

    # Replace the real HTTP request
    monkeypatch.setattr(server.httpx, "get", mock_get)

    # Execute the health checker
    result = server.check_api_health()

    # Verify the returned values
    assert result["status"] == "success"
    assert result["service"] == "example"
    assert result["http_status"] == status_code
    assert result["healthy"] is expected_healthy

    # Verify response-time measurement
    assert isinstance(result["response_time_ms"], float)
    assert result["response_time_ms"] >= 0


def test_check_api_health_rejects_unknown_service(monkeypatch):
    """Verify unknown services are rejected without HTTP requests."""

    # This function must never be called
    def mock_get(*args, **kwargs):
        raise AssertionError(
            "HTTP request should not be made for unknown services"
        )

    # Replace the real HTTP request
    monkeypatch.setattr(server.httpx, "get", mock_get)

    # Try checking an unapproved service
    result = server.check_api_health(service="unknown")

    # Verify the error response
    assert result["status"] == "error"
    assert result["service"] == "unknown"
    assert result["healthy"] is False
    assert result["error_type"] == "invalid_service"
    assert result["message"] == "Service is not approved"


def test_api_health_report_all_healthy(monkeypatch):
    """Verify the report counts healthy services correctly."""

    # Track which services were checked
    checked_services = []

    # Replace the real health checker
    def mock_check_api_health(service="example"):
        checked_services.append(service)

        return {
            "status": "success",
            "service": service,
            "http_status": 200,
            "healthy": True,
            "response_time_ms": 100.0
        }

    monkeypatch.setattr(
        server,
        "check_api_health",
        mock_check_api_health
    )

    # Generate the report
    result = server.get_api_health_report()

    # Verify the summary
    assert result["status"] == "success"
    assert result["total_services"] == 2
    assert result["healthy_services"] == 2
    assert result["unhealthy_services"] == 0

    # Verify both services were checked
    assert set(checked_services) == {"example", "github"}

    # Verify individual results
    assert len(result["services"]) == 2
    assert all(
        item["healthy"] is True
        for item in result["services"]
    )


def test_api_health_report_mixed_health(monkeypatch):
    """Verify the report handles healthy and unhealthy services."""

    # Simulate different health results for each service
    def mock_check_api_health(service="example"):

        if service == "example":
            return {
                "status": "success",
                "service": service,
                "http_status": 200,
                "healthy": True,
                "response_time_ms": 100.0
            }

        return {
            "status": "success",
            "service": service,
            "http_status": 503,
            "healthy": False,
            "response_time_ms": 250.0
        }

    # Replace the real health checker
    monkeypatch.setattr(
        server,
        "check_api_health",
        mock_check_api_health
    )

    # Generate the combined report
    result = server.get_api_health_report()

    # Verify the summary
    assert result["status"] == "success"
    assert result["total_services"] == 2
    assert result["healthy_services"] == 1
    assert result["unhealthy_services"] == 1

    # Verify the individual results
    services = {
        item["service"]: item
        for item in result["services"]
    }

    assert set(services) == {"example", "github"}
    assert services["example"]["healthy"] is True
    assert services["example"]["http_status"] == 200

    assert services["github"]["healthy"] is False
    assert services["github"]["http_status"] == 503


def test_api_health_report_with_timeout(monkeypatch):
    """Verify the report handles a service timeout."""

    # Simulate different results for each service
    def mock_check_api_health(service="example"):

        if service == "example":
            return {
                "status": "success",
                "service": service,
                "http_status": 200,
                "healthy": True,
                "response_time_ms": 100.0
            }

        # Simulate a timeout for github
        return {
            "status": "error",
            "service": service,
            "healthy": False,
            "response_time_ms": 5000.0,
            "error_type": "timeout",
            "message": "API request timed out"
        }

    # Replace the real health checker
    monkeypatch.setattr(
        server,
        "check_api_health",
        mock_check_api_health
    )

    # Generate the report
    result = server.get_api_health_report()

    # Verify the summary
    assert result["status"] == "success"
    assert result["total_services"] == 2
    assert result["healthy_services"] == 1
    assert result["unhealthy_services"] == 1

    # Organize results by service name
    services = {
        item["service"]: item
        for item in result["services"]
    }

    # Verify the healthy service
    assert services["example"]["healthy"] is True
    assert services["example"]["http_status"] == 200

    # Verify the timed-out service
    assert services["github"]["status"] == "error"
    assert services["github"]["healthy"] is False
    assert services["github"]["error_type"] == "timeout"
    assert services["github"]["response_time_ms"] == 5000.0

import json
import psutil
import httpx
import time

from mcp.server.fastmcp import FastMCP
from pathlib import Path
from log_utils import get_log_file_path
from api_config import get_service_url, APPROVED_SERVICES


# Create our MCP server
mcp = FastMCP("InfraMCP")


# Tool 1: Greeting
@mcp.tool()
def say_hello(name: str) -> str:
    """Greet a user by their name."""
    return f"Hello {name}! Welcome to InfraMCP."

#Tool 2: CPU monitoring
@mcp.tool()
def get_cpu_usage() -> dict:
    """Get the current CPU usage percentage."""
    cpu_percent = psutil.cpu_percent(interval=1)
    return {
        "cpu_usage_percent": cpu_percent,
        "status": "success"
    }

#Tool 3: Memory monitoring
@mcp.tool()
def get_memory_usage() -> dict:
    """Get current system RAM usage and available memory."""

    memory = psutil.virtual_memory()

    return {
        "total_memory_gib": round(memory.total / (1024 ** 3), 2),
        "available_memory_gib": round(memory.available / (1024 ** 3), 2),
        "used_memory_percent": memory.percent
    }

#Tool 4: Disk monitoring
@mcp.tool()
def get_disk_usage() -> dict:
    """Get disk storage usage for the root filesystem."""

    disk = psutil.disk_usage("/")

    return {
        "total_disk_gib": round(disk.total / (1024 ** 3), 2),
        "used_disk_gib": round(disk.used / (1024 ** 3), 2),
        "free_disk_gib": round(disk.free / (1024 ** 3), 2),
        "disk_usage_percent": disk.percent
    }

#Tool 5: Read Logs

@mcp.tool()
def read_logs(lines: int = 10) -> dict:
    """Read the most recent entries from the application log."""

    # Locate the log file relative to this Python script
    log_file = get_log_file_path()

    # Validate the requested number of lines
    if not 1 <= lines <= 100:
        return {
            "status": "error",
            "message": "lines must be between 1 and 100"
        }

    # Check whether the log file exists
    if not log_file.is_file():
        return {
            "status": "error",
            "message": "Application log file not found"
        }
        
    try:    
        # Read the file
        with log_file.open("r", encoding="utf-8") as file:
            all_logs = file.readlines()

        # Select the most recent entries
        recent_logs = [
            line.rstrip("\n") 
            for line in all_logs[-lines:]]

        return {
            "status": "success",
            "requested_lines": lines,
            "returned_lines": len(recent_logs),
            "logs": recent_logs
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Application log file not found"
        }
    
    except PermissionError:
        return {
            "status": "error",
            "message": "Permission denied when accessing the log file"
        }
    
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": "Log file contains non-text data or is not UTF-8 encoded"
        }
    
    except OSError:
        return {
            "status": "error",
            "message": "An OS error occurred while reading the log file"
        }

#Tool 6: Search Logs
@mcp.tool()
def search_logs(keyword: str) -> dict:
    """Search application logs for a keyword, ignoring case."""

    log_file = get_log_file_path()

    if not keyword.strip():
        return {
            "status": "error",
            "message": "Search keyword cannot be empty"
        }
        
    if len(keyword) > 100:
        return {
            "status": "error",
            "message": "Search keyword is too long (max 100 characters)"
        }

    try:
        matching_logs = []
        with log_file.open("r", encoding="utf-8") as file:
            for line in file:
                if keyword.casefold() in line.casefold():
                    matching_logs.append(line.rstrip("\n"))

        return {
            "status": "success",
            "keyword": keyword,
            "total_matches": len(matching_logs),
            "logs": matching_logs
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Application log file not found"
        }
    except PermissionError:
        return {
            "status": "error",
            "message": "Permission denied when accessing the log file"
        }
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": "Log file contains non-text data or is not UTF-8 encoded"
        }
    except OSError:
        return {
            "status": "error",
            "message": "An OS error occurred while reading the log file"
        }

#Tool 7: Count Error Events
@mcp.tool()
def count_errors() -> dict:
    """Count ERROR and CRITICAL events in application logs."""

    log_file = get_log_file_path()

    if not log_file.is_file():
        return {
            "status": "error",
            "message": "Application log file not found"
        }

    error_count = 0
    critical_count = 0
    total_logs = 0
    invalid_logs = 0
    
    valid_levels = {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"}

    try:
        with log_file.open("r", encoding="utf-8") as file:
            for line in file:
                parts = line.split(maxsplit=3)

                # Validate the basic log structure
                if len(parts) < 4:
                    invalid_logs += 1
                    continue
                
                date, time, level, message = parts

                # Validate severity level
                level = level.upper()

                if level not in valid_levels:
                    invalid_logs += 1
                    continue
            
                total_logs += 1

                if level == "ERROR":
                    error_count += 1
                elif level == "CRITICAL":
                    critical_count += 1

        return {
            "status": "success",
            "total_logs": total_logs,
            "error_count": error_count,
            "critical_count": critical_count,
            "invalid_logs": invalid_logs,
            "total_error_events": error_count + critical_count
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Application log file not found"
        }
    except PermissionError:
        return {
            "status": "error",
            "message": "Permission denied when accessing the log file"
        }
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": "Log file contains non-text data or is not UTF-8 encoded"
        }
    except OSError:
        return {
            "status": "error",
            "message": "An OS error occurred while reading the log file"
        }

@mcp.tool()
def check_api_health(service: str = "example") -> dict:
    """Check the health and response time of an approved service."""

    # Look up the approved service URL
    url = get_service_url(service)

    # Reject unknown services
    if url is None:
        return {
            "status": "error",
            "service": service,
            "healthy": False,
            "error_type": "invalid_service",
            "message": "Service is not approved"
        }

    start_time = time.perf_counter()

    try:
        response = httpx.get(
            url,
            timeout=5.0,
            follow_redirects=False
        )

        response_time_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        is_healthy = 200 <= response.status_code < 300

        return {
            "status": "success",
            "service": service,
            "http_status": response.status_code,
            "healthy": is_healthy,
            "response_time_ms": response_time_ms
        }

    except httpx.TimeoutException:
        elapsed_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        return {
            "status": "error",
            "service": service,
            "healthy": False,
            "response_time_ms": elapsed_ms,
            "error_type": "timeout",
            "message": "API request timed out"
        }

    except httpx.RequestError:
        elapsed_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        return {
            "status": "error",
            "service": service,
            "healthy": False,
            "response_time_ms": elapsed_ms,
            "error_type": "connection_error",
            "message": "Unable to connect to API"
        }

# Tool 8: Get API Health Report
@mcp.tool()
def get_api_health_report() -> dict:
    """Check all approved services and return a health summary."""

    results = []

    healthy_count = 0
    unhealthy_count = 0

    for service_name in APPROVED_SERVICES:
        result = check_api_health(service=service_name)

        results.append(result)

        if result["healthy"]:
            healthy_count += 1
        else:
            unhealthy_count += 1

    return {
        "status": "success",
        "total_services": len(APPROVED_SERVICES),
        "healthy_services": healthy_count,
        "unhealthy_services": unhealthy_count,
        "services": results
    }
    
# resource: Expose approved services as an MCP resource
@mcp.resource("infra://services")
def get_services_resource() -> str:
    """Expose the approved API services as an MCP Resource."""

    return json.dumps(
        {
            "services": APPROVED_SERVICES
        },
        indent=2
    )
    
@mcp.resource("infra://services/{service_name}")
def get_service_resource(service_name: str) -> str:
    """Return configuration for one approved service."""

    url = get_service_url(service_name)

    if url is None:
        return json.dumps({
            "status": "error",
            "service": service_name,
            "message": "Service is not approved"
        })

    return json.dumps({
        "status": "success",
        "service": service_name,
        "url": url
    }, indent=2)

@mcp.prompt()
def investigate_api_failure(service: str) -> str:
    """Generate troubleshooting instructions for an API service."""

    # Validate the requested service
    url = get_service_url(service)

    if url is None:
        return (
            f"Service '{service}' is not approved. "
            "Ask the user to select a configured service."
        )

    # Generate troubleshooting instructions
    return f"""
Investigate the health of the '{service}' service.

Service URL: {url}

Follow these troubleshooting steps:

1. Use check_api_health to check the service.
2. Review its HTTP status code and response time.
3. If the service is unhealthy, identify whether the
   issue is a timeout, connection failure, or HTTP error.
4. Use get_api_health_report to compare the health
   of other approved services.
5. Summarize the findings and suggest possible
   next troubleshooting steps.

Do not claim a root cause without supporting evidence.
"""

if __name__ == "__main__":
    mcp.run()
# InfraMCP — Infrastructure Monitoring MCP Server

InfraMCP is a Python-based infrastructure monitoring server built using the Model Context Protocol (MCP).

It provides MCP tools for system monitoring, application log analysis, and API health monitoring. It also exposes infrastructure configuration through MCP Resources and offers reusable troubleshooting instructions through MCP Prompts.

The project demonstrates backend development, infrastructure observability, error handling, API integration, and automated testing.

## Tech Stack

- **Language:** Python 3.12
- **MCP Framework:** FastMCP (MCP Python SDK)
- **System Monitoring:** psutil
- **HTTP Client:** HTTPX
- **Testing:** pytest
- **Communication:** MCP over STDIO
- **Version Control:** Git and GitHub

## Features

### Phase 1 — System Monitoring

- Built an MCP server using FastMCP.
- Implemented CPU usage monitoring.
- Implemented memory utilization monitoring.
- Implemented disk usage monitoring.
- Created a terminal-based Python MCP client.
- Integrated MCP Inspector for interactive testing.
- Initialized Git and published the project to GitHub.

### Phase 2 — Application Log Monitoring

- Read recent application log entries.
- Search logs using case-insensitive keywords.
- Count ERROR and CRITICAL events.
- Detect malformed log entries.
- Handle missing log files and invalid UTF-8 data.
- Validate tool inputs and return structured errors.
- Centralize log file path management.
- Add automated unit and MCP integration tests.

### Phase 3 — API Health Monitoring

- Monitor approved HTTP/HTTPS endpoints.
- Check service availability using HTTP status codes.
- Measure response latency in milliseconds.
- Handle timeouts and connection failures.
- Classify HTTP 2xx responses as healthy.
- Restrict monitoring to approved service names.
- Generate combined multi-service health reports.
- Test HTTP failures and report aggregation.

### Phase 4 — MCP Resources and Prompts

- Expose service configuration through MCP Resources.
- Implement static Resource discovery and reading.
- Implement dynamic Resource Templates.
- Retrieve individual service configurations using URI parameters.
- Validate unapproved service names.
- Create reusable API troubleshooting Prompts.
- Support MCP Prompt discovery and retrieval.
- Add MCP integration tests for Resources and Prompts.

## Project Structure

```text
InfraMCP/
├── server.py
├── test_client.py
├── api_config.py
├── log_utils.py
├── logs/
│   └── app.log
├── tests/
│   ├── test_log_utils.py
│   ├── test_log_tools.py
│   ├── test_api_config.py
│   ├── test_api_health.py
│   └── test_mcp_integration.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Main Components

| File | Description |
|------|-------------|
| `server.py` | Main FastMCP server containing tools, Resources, and Prompts |
| `test_client.py` | Terminal-based MCP client |
| `api_config.py` | Approved API service configuration |
| `log_utils.py` | Shared log file path utilities |
| `logs/app.log` | Sample application logs |
| `tests/` | Automated unit and MCP integration tests |
| `requirements.txt` | Python dependencies |

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/InfraMCP.git
cd InfraMCP
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

## Available MCP Tools

InfraMCP currently provides nine MCP tools.

| Tool | Description |
|------|-------------|
| `say_hello` | Returns a greeting |
| `get_cpu_usage` | Returns CPU utilization |
| `get_memory_usage` | Returns memory statistics |
| `get_disk_usage` | Returns disk usage statistics |
| `read_logs` | Reads recent application log entries |
| `search_logs` | Searches logs using a keyword |
| `count_errors` | Counts ERROR and CRITICAL events |
| `check_api_health` | Checks health and latency of an approved API service |
| `get_api_health_report` | Generates a combined health report for all approved services |

## Usage

InfraMCP provides a Python MCP client that communicates with the server using STDIO transport.

The client automatically launches the MCP server.

### System Monitoring

Check CPU usage:

```bash
python test_client.py get_cpu_usage
```

Check memory usage:

```bash
python test_client.py get_memory_usage
```

Check disk usage:

```bash
python test_client.py get_disk_usage
```

### Application Log Monitoring

Read recent logs:

```bash
python test_client.py read_logs
```

Search logs by keyword:

```bash
python test_client.py search_logs database
```

Search for ERROR events:

```bash
python test_client.py search_logs ERROR
```

Count application errors:

```bash
python test_client.py count_errors
```

The log-monitoring tools use the sample log file at `logs/app.log`.

### API Health Monitoring

Check the default service:

```bash
python test_client.py check_api_health
```

Check the GitHub service:

```bash
python test_client.py check_api_health github
```

Test rejection of an unknown service:

```bash
python test_client.py check_api_health unknown
```

Generate a combined API health report:

```bash
python test_client.py get_api_health_report
```

Example health-check response:

```json
{
  "status": "success",
  "service": "github",
  "http_status": 200,
  "healthy": true,
  "response_time_ms": 279.25
}
```

Response times and HTTP status codes depend on the actual network response.

## API Configuration

InfraMCP restricts API monitoring to configured services.

Approved endpoints are defined in `api_config.py`:

```python
APPROVED_SERVICES = {
    "example": "https://example.com",
    "github": "https://github.com",
}
```

The `check_api_health` tool accepts a service name instead of an arbitrary URL.

If no service is specified, `example` is used by default.

Unknown service names are rejected before making an HTTP request.

These public websites are demonstration targets, not dedicated application health endpoints.

For production deployment, additional network security controls and appropriate service health endpoints should be configured.

## MCP Resources

InfraMCP exposes infrastructure configuration using MCP Resources.

Resources allow MCP clients to discover and retrieve information through resource URIs.

### Static Resource

**URI:** `infra://services`

Returns all configured approved services.

Example response:

```json
{
  "services": {
    "example": "https://example.com",
    "github": "https://github.com"
  }
}
```

### Dynamic Resource Template

**URI:** `infra://services/{service_name}`

Returns configuration for an individual approved service.

Example URI:

```text
infra://services/github
```

Example response:

```json
{
  "status": "success",
  "service": "github",
  "url": "https://github.com"
}
```

An unknown service returns:

```json
{
  "status": "error",
  "service": "unknown",
  "message": "Service is not approved"
}
```

Resource reading does not make external HTTP requests. It retrieves information from the local service configuration.

### Resource Operations

| MCP Operation | Purpose |
|---------------|---------|
| `resources/list` | Discover static Resources |
| `resources/read` | Retrieve Resource contents |
| `resources/templates/list` | Discover dynamic Resource Templates |

## MCP Prompts

InfraMCP provides reusable troubleshooting instructions through MCP Prompts.

### investigate_api_failure

Generates troubleshooting instructions for an approved API service.

**Required argument:** `service`

Example:

```text
Prompt: investigate_api_failure
Service: github
```

The generated prompt guides an AI assistant to:

1. Check the service using `check_api_health`.
2. Review HTTP status codes and response latency.
3. Identify timeouts, connection failures, or HTTP errors.
4. Compare services using `get_api_health_report`.
5. Summarize findings and suggest troubleshooting steps.

The prompt also instructs the assistant not to claim a root cause without supporting evidence.

Unknown service names receive a validation message.

Retrieving an MCP Prompt does not automatically execute monitoring tools or invoke an AI model.

### Prompt Operations

| MCP Operation | Purpose |
|---------------|---------|
| `prompts/list` | Discover available Prompts |
| `prompts/get` | Retrieve generated Prompt instructions |

## MCP Capabilities

InfraMCP currently supports all three major MCP capability types.

| Capability | Count | Description |
|------------|-------|-------------|
| Tools | 9 | System, log, and API monitoring |
| Static Resources | 1 | Approved service inventory |
| Resource Templates | 1 | Individual service configuration |
| Prompts | 1 | API failure investigation |

All capabilities are exposed through the FastMCP server.

## Testing

InfraMCP uses pytest for automated unit and integration testing.

The test suite covers:

- Log file path utilities
- Log reading, searching, and error counting
- Input validation and malformed log entries
- Missing files and invalid UTF-8 data
- HTTP status classification
- API timeouts and connection failures
- Approved service validation
- Multi-service health report aggregation
- MCP tool discovery and execution
- MCP Resource discovery and reading
- Dynamic Resource Template discovery and reading
- MCP Prompt discovery and retrieval
- Unknown service validation

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run Log Monitoring Tests

```bash
python -m pytest tests/test_log_tools.py -v
```

### Run API Monitoring Tests

```bash
python -m pytest tests/test_api_health.py -v
```

### Run MCP Integration Tests

```bash
python -m pytest tests/test_mcp_integration.py -v
```

**Current test suite: 44 passing tests.**

## MCP Inspector

InfraMCP can be explored interactively using MCP Inspector.

Start the Inspector:

```bash
mcp dev server.py
```

If the Inspector does not start correctly, ensure Node.js and npm are configured properly.

The Inspector can be used to discover and interact with supported MCP Tools, Resources, and Prompts.

## Roadmap

- [x] Phase 1: MCP server and system monitoring
- [x] Phase 2: Application log monitoring
- [x] Phase 3: API health monitoring
- [x] Phase 4: MCP Resources and Prompts
- [ ] Phase 5: PostgreSQL database integration
- [ ] Phase 6: Docker container monitoring
- [ ] Phase 7: AWS infrastructure monitoring
- [ ] Phase 8: Production deployment and CI/CD

## Future Improvements

Planned enhancements include:

- PostgreSQL database health monitoring
- Safe read-only database inspection
- Docker container monitoring
- AWS EC2 and CloudWatch integration
- Structured application logging
- Improved configuration and security controls
- Concurrent infrastructure health checks
- Dockerized deployment
- GitHub Actions CI/CD
- Remote MCP server deployment

## Project Status

**Phases 1 through 4 are implemented and tested.**

InfraMCP currently includes:

- 9 MCP monitoring tools
- 1 static MCP Resource
- 1 dynamic Resource Template
- 1 reusable MCP Prompt
- 44 automated unit and integration tests

The project demonstrates MCP server development, system observability, application log analysis, API monitoring, configuration discovery, and automated testing.

**Status:** Active development.

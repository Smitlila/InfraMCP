
# InfraMCP

A Python-based Model Context Protocol (MCP) server for
infrastructure monitoring and developer automation.

InfraMCP is a learning project that starts with basic
system monitoring and will gradually expand to support
log analysis, API monitoring, Docker, and cloud infrastructure.

## Features


### Phase 1 - System Monitoring

- CPU usage monitoring
- Memory usage monitoring
- Disk storage monitoring
- MCP tool discovery and execution
- Terminal-based MCP client
- MCP Inspector integration

### Phase 2 - Application Log Monitoring

- Read recent application log entries
- Search logs using case-insensitive keywords
- Count ERROR and CRITICAL events
- Detect malformed log entries
- Handle missing files and invalid UTF-8 data
- Validate tool inputs
- Centralized log file path management
- Automated unit and MCP integration testing

### Phase 3 - API Health Monitoring

- Monitor approved HTTP/HTTPS endpoints
- Check API availability using HTTP status codes
- Measure response time in milliseconds
- Handle request timeouts and connection failures
- Classify HTTP 2xx responses as healthy
- Reject unapproved service names
- Monitor multiple services through a single MCP tool
- Generate combined health reports
- Automated unit and MCP integration testing

## Tech Stack

- Python 3.12
- MCP Python SDK (1.x)
- psutil
- asyncio
- MCP Inspector

## Project Structure

```text

InfraMCP/
├── server.py
├── test_client.py
├── log_utils.py
├── api_config.py
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

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd InfraMCP
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `say_hello` | Returns a greeting |
| `get_cpu_usage` | Returns current CPU usage |
| `get_memory_usage` | Returns memory statistics |
| `get_disk_usage` | Returns disk usage statistics |
| `read_logs` | Reads recent application log entries |
| `search_logs` | Searches logs using a keyword |
| `count_errors` | Counts ERROR and CRITICAL log events |
| `check_api_health` | Checks the health and latency of an approved service |
| `get_api_health_report` | Generates a combined report for all approved services |

## Usage

InfraMCP provides a Python MCP client for executing tools
directly from the terminal.

### System Monitoring

```bash
python test_client.py get_cpu_usage
python test_client.py get_memory_usage
python test_client.py get_disk_usage
python test_client.py say_hello Alex
```

### Application Log Monitoring

```bash
python test_client.py read_logs
python test_client.py search_logs database
python test_client.py search_logs ERROR
python test_client.py count_errors
```

The client automatically starts the MCP server using
STDIO transport.

The log-monitoring tools read from `logs/app.log`.


## MCP Inspector

InfraMCP can also be tested using MCP Inspector.

Configure a local STDIO server with:

- Command: Path to the project's virtual environment Python
- Arguments: Path to server.py
- Transport: STDIO

The MCP client starts the server automatically.

## Roadmap

- [x] Phase 1: Basic MCP server and system monitoring
- [x] Phase 2: Application log analysis
- [x] Phase 3: API health monitoring
- [ ] Phase 4: MCP resources and prompts
- [ ] Phase 5: Database integration
- [ ] Phase 6: Docker monitoring
- [ ] Phase 7: AWS infrastructure monitoring
- [ ] Phase 8: Production deployment


## Project Status

Phases 1, 2, and 3 are implemented and tested.

InfraMCP currently provides nine MCP tools for
system monitoring, application log analysis, and
API health monitoring.

The project includes 36 automated tests covering
unit-level behavior and MCP integration.

The project is under active development.




## Testing

InfraMCP uses pytest for automated testing.

The test suite covers:

- System and log utility functionality
- Application log reading and searching
- Input validation and error handling
- Missing files and invalid UTF-8 data
- API health monitoring and HTTP status classification
- API timeouts and connection failures
- Approved service validation
- Multi-service health report aggregation
- MCP client-server integration

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run API Monitoring Tests

```bash
python -m pytest tests/test_api_health.py -v
```

### Run MCP Integration Tests

```bash
python -m pytest tests/test_mcp_integration.py -v
```

Current test suite: 36 passing tests.



## API Configuration

InfraMCP uses an allowlist of approved services.

Approved endpoints are configured in `api_config.py`:

```python
APPROVED_SERVICES = {
    "example": "https://example.com",
    "github": "https://github.com",
}
```

The `check_api_health` tool accepts a service name
instead of an arbitrary URL.

If no service is provided, `example` is used by default.

Unknown service names are rejected before an HTTP
request is made.

These public websites are demonstration targets,
not dedicated application health endpoints.

For production use, configure appropriate health
endpoints and enforce additional network security controls.


### API Health Monitoring

Check the default service:

```bash
python test_client.py check_api_health
```

Check an approved service:

```bash
python test_client.py check_api_health github
```

Test rejection of an unknown service:

```bash
python test_client.py check_api_health unknown
```

Generate a combined health report:

```bash
python test_client.py get_api_health_report
```

The API monitoring tools report HTTP status codes,
service health, and response times in milliseconds.

Only configured services can be monitored.

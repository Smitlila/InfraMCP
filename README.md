
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
├── logs/
│   └── app.log
├── tests/
│   ├── test_log_utils.py
│   ├── test_log_tools.py
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
| `get_memory_usage` | Returns RAM statistics |
| `get_disk_usage` | Returns disk storage statistics |
| `read_logs` | Returns recent application log entries |
| `search_logs` | Searches logs using a keyword |
| `count_errors` | Counts ERROR and CRITICAL log events |


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
- [ ] Phase 3: API health monitoring
- [ ] Phase 4: MCP resources and prompts
- [ ] Phase 5: Database integration
- [ ] Phase 6: Docker monitoring
- [ ] Phase 7: AWS integration
- [ ] Phase 8: Production deployment


## Project Status

Phase 1 and Phase 2 implemented and tested.

InfraMCP currently provides seven MCP tools for system
monitoring and application log analysis, supported by
20 automated unit and integration tests.

The project is under active development.



## Testing

InfraMCP uses pytest for automated testing.

The test suite includes:

- Unit tests for log file path utilities
- Unit tests for log reading, searching, and error counting
- Input validation and failure scenario tests
- Missing-file and invalid UTF-8 handling tests
- MCP tool discovery integration tests
- MCP tool execution integration tests

### Run All Tests

```bash
python -m pytest tests/ -v
```

### Run a Specific Test File

```bash
python -m pytest tests/test_log_tools.py -v
```

### Run MCP Integration Tests

```bash
python -m pytest tests/test_mcp_integration.py -v
```

Current test suite: 20 passing tests.

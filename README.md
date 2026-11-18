
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
| say_hello | Returns a greeting |
| get_cpu_usage | Returns current CPU usage |
| get_memory_usage | Returns RAM statistics |
| get_disk_usage | Returns disk storage statistics |

## Usage

Run tools through the Python MCP client:

```bash
python test_client.py get_cpu_usage
python test_client.py get_memory_usage
python test_client.py get_disk_usage
python test_client.py say_hello Alex
```

The client automatically starts the MCP server
using STDIO transport.

## MCP Inspector

InfraMCP can also be tested using MCP Inspector.

Configure a local STDIO server with:

- Command: Path to the project's virtual environment Python
- Arguments: Path to server.py
- Transport: STDIO

The MCP client starts the server automatically.

## Roadmap

- [x] Phase 1: Basic MCP server and system monitoring
- [ ] Phase 2: Application log analysis
- [ ] Phase 3: API health monitoring
- [ ] Phase 4: MCP resources and prompts
- [ ] Phase 5: Database integration
- [ ] Phase 6: Docker monitoring
- [ ] Phase 7: AWS integration
- [ ] Phase 8: Production deployment

## Project Status

Phase 1 completed.

This project is being developed incrementally
to explore MCP architecture, infrastructure
monitoring, and developer automation.

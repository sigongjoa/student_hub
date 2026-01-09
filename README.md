# Node 0: Student Hub

Implementation of the Student Hub orchestrator node.

## Directory Structure
- `api/`: REST API endpoints
- `core/`: Business logic (StudentManager, ProfileAggregator, etc.)
- `mcp_client/`: Client for communicating with other MCP nodes
- `repositories/`: Data access layer (Postgres/Redis)
- `models/`: Pydantic data models
- `tests/`: Verification scripts

## Running
To start the FastAPI server:
```bash
uvicorn node0_student_hub.main:app --reload --port 8000
```

## Testing
Run the verification script:
```bash
python3 node0_student_hub/tests/test_flow.py
```

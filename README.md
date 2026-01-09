# Node 0: Student Hub - Master Orchestrator Node

> Single Source of Truth for student data + Workflow automation across all nodes

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

**Node 0 (Student Hub)** is the **master orchestrator node** in the Mathesis platform. It serves as:

1. **Single Source of Truth (SSOT)**: All student data centralized here
2. **Workflow Orchestrator**: Automates educational workflows across nodes
3. **MCP Client**: Communicates with all other nodes via MCP protocol
4. **Profile Aggregator**: Combines data from all nodes into unified student profiles

### Why Node 0?

- **Data Consistency**: One place for student demographic, enrollment, and master data
- **Workflow Automation**: Chains operations across multiple nodes seamlessly
- **Cross-Node Coordination**: Handles complex educational workflows
- **Performance**: Caches frequently accessed student data (Redis)

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│           Node 0: Student Hub (Master Node)              │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         FastAPI REST API                        │    │
│  │  - Student CRUD                                 │    │
│  │  - Profile aggregation                          │    │
│  │  - Workflow triggers                            │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Core Business Logic                     │    │
│  │  - StudentManager                               │    │
│  │  - ProfileAggregator                            │    │
│  │  - WorkflowOrchestrator                         │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         MCP Client                              │    │
│  │  - Node 1 (Logic Engine)                       │    │
│  │  - Node 2 (Q-DNA)                              │    │
│  │  - Node 4 (Lab Node)                           │    │
│  │  - Node 5 (Report Node)                        │    │
│  │  - Node 6 (School Info)                        │    │
│  │  - Node 7 (Error Note)                         │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Data Layer                              │    │
│  │  - PostgreSQL (SSOT)                           │    │
│  │  - Redis (Cache)                               │    │
│  └────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.11+
PostgreSQL 14+
Redis 6+
MCP-compatible nodes (Node 1-7)
```

### Installation

```bash
# 1. Install dependencies
cd node0_student_hub
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env  # Edit with your settings

# 3. Setup database
# Create PostgreSQL database
createdb student_hub

# Run migrations (if using Alembic)
alembic upgrade head

# 4. Start Redis
redis-server

# 5. Start FastAPI server
uvicorn node0_student_hub.main:app --reload --port 8000
```

## 📡 API Endpoints

### Student Management

```bash
# Create student
POST /api/v1/students/
{
  "student_id": "student_123",
  "name": "김철수",
  "grade": 10,
  "school_id": "school_456"
}

# Get student profile (aggregated from all nodes)
GET /api/v1/students/{student_id}/profile
# Returns: {
#   "basic_info": {...},
#   "q_dna_mastery": {...},  # From Node 2
#   "error_patterns": {...},  # From Node 7
#   "lab_progress": {...},    # From Node 4
#   "recent_reports": [...]   # From Node 5
# }

# Update student
PATCH /api/v1/students/{student_id}

# Delete student
DELETE /api/v1/students/{student_id}
```

### Workflow Orchestration

```bash
# Trigger diagnostic workflow
POST /api/v1/workflows/diagnostic
{
  "student_id": "student_123",
  "curriculum_path": "고등수학.미적분"
}
# Orchestrates:
# 1. Node 2: Get recommended questions based on BKT
# 2. Node 4: Track lab activity
# 3. Node 7: Record errors
# 4. Node 5: Generate diagnostic report

# Trigger learning path workflow
POST /api/v1/workflows/learning-path
{
  "student_id": "student_123",
  "target_concepts": ["도함수", "적분"]
}
```

### Profile Aggregation

```bash
# Get complete student profile
GET /api/v1/profiles/{student_id}
# Aggregates data from:
# - Node 0: Basic info, enrollment
# - Node 2: Mastery levels (BKT)
# - Node 4: Lab completion
# - Node 7: Error patterns
```

## 🗄️ Data Models

### Student (SSOT)

```python
class Student:
    student_id: str         # Primary identifier
    name: str
    grade: int             # 1-12
    school_id: str
    enrollment_date: date
    status: str            # active, inactive, graduated
    metadata: Dict         # Flexible additional data
```

### StudentProfile (Aggregated)

```python
class StudentProfile:
    student_id: str
    basic_info: Student
    q_dna_summary: Dict    # From Node 2
    error_summary: Dict    # From Node 7
    lab_summary: Dict      # From Node 4
    reports: List[Report]  # From Node 5
    last_updated: datetime
```

## 🔄 Workflow Examples

### Example 1: Weekly Diagnostic

```python
# Triggered by scheduler or API
workflow = WorkflowOrchestrator()

result = await workflow.run_diagnostic(
    student_id="student_123",
    week_number=5
)

# Steps:
# 1. Get student mastery from Node 2
# 2. Recommend 10 questions based on BKT
# 3. Track student attempts in Node 4
# 4. Analyze errors in Node 7
# 5. Generate weekly report in Node 5
# 6. Cache results in Redis
```

### Example 2: Error Recovery Path

```python
# When student makes repeated errors
workflow = WorkflowOrchestrator()

result = await workflow.run_error_recovery(
    student_id="student_123",
    error_note_id=456
)

# Steps:
# 1. Get error analysis from Node 7
# 2. Request similar problems from Node 2
# 3. Generate twin variations (Node 2 + mathesis_core)
# 4. Create practice lab in Node 4
# 5. Schedule review in Node 7 (Anki)
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/ -v

# Run integration tests (requires all nodes running)
pytest tests/integration/ -v

# Test workflow
python tests/test_flow.py
```

## 📊 Performance Considerations

### Caching Strategy

- **Redis**: Student profiles cached for 5 minutes
- **MCP Calls**: Timeout 30 seconds with retry (3 attempts)
- **Aggregation**: Parallel calls to all nodes

### Scalability

- **Horizontal**: Multiple Node 0 instances with shared Redis/Postgres
- **Load Balancing**: Round-robin across Node 0 instances
- **Database**: Connection pooling (10-50 connections)

## 🔗 Node Communication

### MCP Client Usage

```python
from mcp_client import MCPClientManager

# Initialize MCP clients
mcp = MCPClientManager()

# Call Node 2 (Q-DNA)
mastery = await mcp.call("q-dna", "get_student_mastery", {
    "student_id": "student_123"
})

# Call Node 7 (Error Note)
errors = await mcp.call("error-note", "get_error_patterns", {
    "student_id": "student_123",
    "time_range": "last_30_days"
})
```

## 📚 Documentation

- [Technical Design](../../docs/nodes/NODE0_STUDENT_HUB.md)
- [API Documentation](http://localhost:8000/docs) - Swagger UI
- [Workflow Patterns](../../docs/workflows/)

## 🤝 Contributing

### Code Standards

- **Type Hints**: Required
- **Docstrings**: Google style
- **Async/Await**: For all I/O operations
- **Testing**: 90%+ coverage

## 🔗 Related Projects

- [Node 2 (Q-DNA)](https://github.com/sigongjoa/q-dna) - Question bank
- [Node 7 (Error Note)](https://github.com/sigongjoa/error-note) - Error analysis

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

**Last Updated**: 2026-01-10
**Version**: 1.0
**Port**: 8000
**Status**: 🚧 Design Phase

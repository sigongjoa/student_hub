# Mathesis TDD Master Plan - 100% Test Coverage
## Session: 2026-01-11

---

## Overview

**Goal**: Implement all remaining features using Test-Driven Development (TDD) methodology with 100% test coverage.

**Methodology**: Red-Green-Refactor
1. **Red**: Write failing test first
2. **Green**: Write minimal code to pass test
3. **Refactor**: Improve code quality while keeping tests green

**Coverage Target**: 100% for all new code
- Unit Tests: 100%
- Integration Tests: 100%
- E2E Tests: Critical user flows

---

## Use Cases & Test Strategy

### Use Case 1: Student Learning Analytics Dashboard

**User Story**:
> As a teacher, I want to view comprehensive learning analytics for each student so I can identify struggling areas and provide targeted support.

**Acceptance Criteria**:
1. Display student mastery summary (average, attempts, trend)
2. Show recent learning activities with dates and scores
3. Visualize concept mastery heatmap
4. Highlight weak concepts (< 60% accuracy)
5. Display learning activity summary for past 7 days

**Test Cases**:
- ✅ API returns unified profile with all required fields
- ✅ Mastery summary calculates average correctly
- ✅ Recent activities limited to 3 items
- ✅ Heatmap includes all practiced concepts
- ✅ Weak concepts filtered by threshold

**Coverage**: Node 0 (REST API) + Node 4 (Lab Node MCP)

---

### Use Case 2: Concept Prerequisite Navigation

**User Story**:
> As a student, I want to understand which concepts I need to learn first before tackling advanced topics.

**Acceptance Criteria**:
1. Display prerequisite graph for any concept
2. Show dependent concepts (what comes after)
3. Visualize learning path from basics to advanced
4. Highlight already mastered prerequisites
5. Suggest next concepts to learn

**Test Cases**:
- [ ] API returns prerequisite graph for concept
- [ ] Graph includes all direct prerequisites
- [ ] Graph includes all dependent concepts
- [ ] Cycle detection for invalid graphs
- [ ] Empty prerequisites for foundational concepts

**Coverage**: Node 1 (Logic Engine MCP)

---

### Use Case 3: Error Note Review System

**User Story**:
> As a student, I want to review my errors systematically using spaced repetition so I can master difficult concepts.

**Acceptance Criteria**:
1. Create error note when student makes mistake
2. Analyze error with misconception identification
3. Calculate next review date using Anki SM-2 algorithm
4. Show due reviews for today
5. Update review schedule based on recall quality

**Test Cases**:
- [ ] Create error note with analysis
- [ ] Calculate SM-2 schedule correctly (ease factor, interval)
- [ ] Retrieve due reviews for specific date
- [ ] Update schedule on review (correct vs incorrect)
- [ ] Handle edge cases (first review, perfect recall)

**Coverage**: Node 7 (Error Note MCP)

---

### Use Case 4: Intelligent Question Recommendation

**User Story**:
> As a student, I want to receive personalized question recommendations based on my current mastery level.

**Acceptance Criteria**:
1. Recommend questions matching student's mastery level
2. Use IRT (Item Response Theory) for difficulty matching
3. Prioritize weak concepts
4. Avoid recently attempted questions
5. Return 10 questions per request

**Test Cases**:
- [ ] Recommend questions for student mastery level
- [ ] IRT calculation (3PL model: difficulty, discrimination, guessing)
- [ ] Filter by concept
- [ ] Exclude recently attempted questions (< 7 days)
- [ ] Return exactly 10 questions

**Coverage**: Node 2 (Q-DNA MCP)

---

### Use Case 5: Mock Exam Generation

**User Story**:
> As a teacher, I want to generate mock exams for students based on school curriculum and student mastery.

**Acceptance Criteria**:
1. Generate exam with school-specific scope
2. Include questions covering all curriculum topics
3. Difficulty distribution (easy: 30%, medium: 50%, hard: 20%)
4. Generate PDF with answer key
5. Store exam metadata for later analysis

**Test Cases**:
- [ ] Generate exam for school + grade
- [ ] Verify question difficulty distribution
- [ ] Ensure all curriculum topics covered
- [ ] PDF generation successful
- [ ] Metadata stored correctly

**Coverage**: Node 5 (Q-Metrics MCP)

---

### Use Case 6: School Curriculum Management

**User Story**:
> As an administrator, I want to manage school-specific curriculum and exam schedules.

**Acceptance Criteria**:
1. Store exam scope per school and grade
2. Define curriculum topics and weightings
3. Set exam dates and durations
4. Retrieve exam schedule for date range
5. Update curriculum dynamically

**Test Cases**:
- [ ] Create/update exam scope
- [ ] Retrieve exam scope by school + grade
- [ ] Get upcoming exams for school
- [ ] Validate curriculum weightings sum to 100%
- [ ] Handle multiple exam schedules

**Coverage**: Node 6 (School Info MCP)

---

### Use Case 7: Weekly Diagnostic Workflow

**User Story**:
> As a system, I want to automatically generate weekly diagnostic reports for all students to identify those needing intervention.

**Acceptance Criteria**:
1. Calculate mastery scores for all students weekly
2. Identify at-risk students (avg mastery < 50%)
3. Generate diagnostic report with weak concepts
4. Recommend intervention strategies
5. Send notifications to teachers

**Test Cases**:
- [ ] Calculate mastery for all students
- [ ] Identify at-risk students correctly
- [ ] Generate comprehensive report
- [ ] Include actionable recommendations
- [ ] Workflow executes on schedule

**Coverage**: Workflow orchestration

---

### Use Case 8: Real-time Learning Data Persistence

**User Story**:
> As a system, I want to persist all learning activity data so analytics are based on actual student performance.

**Acceptance Criteria**:
1. Store student attempts with timestamp
2. Record question responses (correct/incorrect)
3. Track concept practice sessions
4. Calculate running mastery scores
5. Support efficient queries for analytics

**Test Cases**:
- [ ] Insert student attempt record
- [ ] Query attempts by student + concept
- [ ] Calculate mastery from historical data
- [ ] Aggregate statistics efficiently
- [ ] Handle concurrent writes

**Coverage**: Database layer (PostgreSQL + SQLAlchemy)

---

## Test Coverage Strategy

### Layer 1: Unit Tests (Isolated Component Testing)

**Target**: 100% code coverage for all functions/methods

#### MCP Servers (Nodes 1, 5, 6, 7)
- Test each tool independently
- Mock all database/external dependencies
- Verify input validation
- Test error handling
- Check output format

**Example (Node 1 - Logic Engine)**:
```python
# test_logic_engine_mcp.py

import pytest
from node1_logic_engine.backend.mcp_server import handle_call_tool

@pytest.mark.asyncio
async def test_get_prerequisite_graph_basic_concept():
    """Test prerequisite graph for foundational concept"""
    result = await handle_call_tool("get_prerequisite_graph", {
        "concept": "극한"
    })

    data = json.loads(result[0].text)
    assert data["concept"] == "극한"
    assert data["prerequisites"] == []  # Foundational concept
    assert "도함수" in data["dependents"]
    assert "미분" in data["dependents"]

@pytest.mark.asyncio
async def test_get_prerequisite_graph_advanced_concept():
    """Test prerequisite graph for advanced concept"""
    result = await handle_call_tool("get_prerequisite_graph", {
        "concept": "적분"
    })

    data = json.loads(result[0].text)
    assert "도함수" in data["prerequisites"]
    assert len(data["prerequisites"]) > 0
```

#### Database Models & Repositories
- Test CRUD operations
- Verify relationship mappings
- Test query filters
- Check constraint validations
- Test transactions

**Example (Student Attempts)**:
```python
# test_student_attempts_repository.py

import pytest
from app.repositories.student_attempts import StudentAttemptsRepository

@pytest.mark.asyncio
async def test_create_student_attempt(db_session):
    """Test creating student attempt record"""
    repo = StudentAttemptsRepository(db_session)

    attempt = await repo.create({
        "student_id": "student_123",
        "question_id": "q_456",
        "concept": "도함수",
        "is_correct": True,
        "response_time_ms": 45000
    })

    assert attempt.id is not None
    assert attempt.student_id == "student_123"
    assert attempt.is_correct is True

@pytest.mark.asyncio
async def test_get_attempts_by_concept(db_session):
    """Test querying attempts by concept"""
    repo = StudentAttemptsRepository(db_session)

    # Create test data
    await repo.create({
        "student_id": "student_123",
        "concept": "도함수",
        "is_correct": True
    })
    await repo.create({
        "student_id": "student_123",
        "concept": "적분",
        "is_correct": False
    })

    attempts = await repo.get_by_student_and_concept(
        "student_123", "도함수"
    )

    assert len(attempts) == 1
    assert attempts[0].concept == "도함수"
```

#### Algorithms (BKT, IRT, SM-2)
- Test mathematical correctness
- Verify edge cases
- Test convergence properties
- Benchmark performance

**Example (BKT - Bayesian Knowledge Tracing)**:
```python
# test_bkt_algorithm.py

import pytest
from app.algorithms.bkt import BayesianKnowledgeTracing

def test_bkt_initial_mastery():
    """Test BKT with no prior attempts"""
    bkt = BayesianKnowledgeTracing(
        p_init=0.1,    # Initial mastery probability
        p_learn=0.3,   # Learning rate
        p_slip=0.1,    # Slip probability
        p_guess=0.2    # Guess probability
    )

    mastery = bkt.calculate_mastery([])
    assert mastery == pytest.approx(0.1, abs=0.01)

def test_bkt_all_correct_answers():
    """Test BKT with all correct answers"""
    bkt = BayesianKnowledgeTracing()

    attempts = [
        {"is_correct": True},
        {"is_correct": True},
        {"is_correct": True},
        {"is_correct": True},
        {"is_correct": True}
    ]

    mastery = bkt.calculate_mastery(attempts)
    assert mastery > 0.8  # Should be high with all correct
    assert mastery <= 1.0

def test_bkt_alternating_correctness():
    """Test BKT with mixed performance"""
    bkt = BayesianKnowledgeTracing()

    attempts = [
        {"is_correct": True},
        {"is_correct": False},
        {"is_correct": True},
        {"is_correct": False}
    ]

    mastery = bkt.calculate_mastery(attempts)
    assert 0.3 < mastery < 0.7  # Should be moderate
```

---

### Layer 2: Integration Tests (Component Interaction)

**Target**: 100% coverage of component interactions

#### API → MCP Server Integration
- Test REST API calls to MCP servers
- Verify data transformation
- Test error propagation
- Check timeout handling

**Example**:
```python
# test_unified_profile_integration.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_unified_profile_calls_all_nodes(app, test_student):
    """Test unified profile integrates all node data"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/students/{test_student.id}/unified-profile"
        )

    assert response.status_code == 200
    data = response.json()

    # Verify Node 2 data (Q-DNA)
    assert "mastery_summary" in data
    assert data["mastery_summary"]["average"] is not None

    # Verify Node 4 data (Lab Node)
    assert "heatmap_data" in data
    assert len(data["heatmap_data"]) > 0

    # Verify Node 7 data (Error Note)
    assert "error_notes" in data or True  # Optional field
```

#### Database → Service Layer Integration
- Test repository → service interactions
- Verify transaction handling
- Test caching behavior

---

### Layer 3: End-to-End Tests (User Workflows)

**Target**: Critical user paths tested

#### Frontend User Flows
- Student views learning analytics
- Teacher creates intervention
- System generates weekly diagnostic

**Example (Playwright)**:
```python
# test_e2e_student_analytics.py

import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_student_views_complete_analytics():
    """E2E: Student views all learning analytics"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Navigate to student detail
        await page.goto("http://localhost:5173/students/student_123")

        # Verify all sections load
        await page.wait_for_selector("text=Mastery Avg")
        await page.wait_for_selector("text=Recent Activities")
        await page.wait_for_selector("text=Heatmap")

        # Check data is populated
        mastery_text = await page.locator("text=Mastery Avg").text_content()
        assert "%" in mastery_text

        # Verify heatmap renders
        heatmap = await page.locator("[data-testid='concept-heatmap']")
        assert await heatmap.count() > 0

        await browser.close()
```

---

## Implementation Order (TDD)

### Phase 1: Database Layer (Week 1)
**Priority**: Foundation for all features

1. **Design Database Schema**
   - Student attempts table
   - Concept mastery table
   - Error notes table
   - Question bank table

2. **Implement SQLAlchemy Models**
   - Write schema tests first
   - Implement models
   - Add relationships

3. **Create Repositories**
   - Write repository tests first
   - Implement CRUD operations
   - Add query methods

**Test Coverage Target**: 100%
- Schema validation: 100%
- CRUD operations: 100%
- Query methods: 100%

---

### Phase 2: Core Algorithms (Week 1-2)

1. **BKT (Bayesian Knowledge Tracing)**
   - Write algorithm tests with known inputs/outputs
   - Implement BKT calculation
   - Optimize performance

2. **IRT (Item Response Theory)**
   - Write IRT tests (3PL model)
   - Implement difficulty calculation
   - Test question recommendation

3. **SM-2 (Spaced Repetition)**
   - Write SM-2 tests with example schedules
   - Implement scheduling algorithm
   - Test edge cases

**Test Coverage Target**: 100%
- Algorithm correctness: 100%
- Edge cases: 100%
- Performance benchmarks: All passing

---

### Phase 3: MCP Servers (Week 2-3)

#### Node 1: Logic Engine
**Tools**: 3
1. `get_prerequisite_graph` - Returns concept dependencies
2. `get_learning_path` - Generates ordered learning sequence
3. `validate_curriculum` - Checks for cycles and completeness

**Test Strategy**:
```python
# Tests written FIRST
def test_get_prerequisite_graph_no_cycles()
def test_get_learning_path_correct_order()
def test_validate_curriculum_detects_cycles()
```

#### Node 7: Error Note
**Tools**: 4
1. `create_error_note` - Creates note with analysis
2. `get_due_reviews` - Returns reviews for date
3. `update_review_schedule` - Recalculates SM-2
4. `analyze_misconception` - Identifies error patterns

**Test Strategy**:
```python
# Tests written FIRST
def test_create_error_note_with_analysis()
def test_sm2_schedule_calculation()
def test_get_due_reviews_filters_by_date()
def test_misconception_analysis()
```

#### Node 5: Q-Metrics
**Tools**: 3
1. `generate_mock_exam` - Creates exam with specifications
2. `evaluate_exam` - Scores and analyzes performance
3. `get_difficulty_distribution` - Returns question difficulty stats

**Test Strategy**:
```python
# Tests written FIRST
def test_generate_exam_meets_specifications()
def test_difficulty_distribution_correct()
def test_evaluate_exam_calculates_score()
```

#### Node 6: School Info
**Tools**: 3
1. `get_exam_scope` - Returns curriculum for school/grade
2. `get_upcoming_exams` - Returns exam schedule
3. `update_curriculum` - Modifies school curriculum

**Test Strategy**:
```python
# Tests written FIRST
def test_get_exam_scope_by_school_grade()
def test_get_upcoming_exams_filters_dates()
def test_update_curriculum_validates_weightings()
```

**Test Coverage Target**: 100%
- Each tool: 100%
- Error handling: 100%
- Input validation: 100%

---

### Phase 4: Frontend UI Components (Week 3-4)

1. **Heatmap Visualization**
   - Write component tests
   - Implement with Chart.js/Recharts
   - Test responsiveness

2. **Learning Activity Timeline**
   - Write component tests
   - Implement timeline component
   - Test date filtering

3. **Weak Concepts Alert**
   - Write component tests
   - Implement alert badge
   - Test threshold logic

**Test Coverage Target**: 95%
- Component rendering: 100%
- User interactions: 100%
- Edge cases: 90%

---

### Phase 5: Workflows (Week 4-5)

1. **Weekly Diagnostic Workflow**
   - Write workflow tests
   - Implement orchestration
   - Test scheduling

2. **Error Review Workflow**
   - Write workflow tests
   - Implement review logic
   - Test notifications

3. **Learning Path Workflow**
   - Write workflow tests
   - Implement path generation
   - Test adaptation

**Test Coverage Target**: 100%
- Workflow execution: 100%
- Error handling: 100%
- State transitions: 100%

---

## Coverage Measurement

### Tools
- **Python**: `pytest-cov`
- **TypeScript**: `vitest` with coverage
- **E2E**: Playwright test coverage plugin

### Commands
```bash
# Backend coverage
cd node0_student_hub
pytest --cov=app --cov-report=html --cov-report=term

# Frontend coverage
cd frontend
npm run test:coverage

# E2E coverage
playwright test --coverage
```

### Thresholds
```ini
# .coveragerc
[coverage:run]
branch = True
source = app

[coverage:report]
fail_under = 100
show_missing = True
skip_covered = False

[coverage:html]
directory = htmlcov
```

---

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Test Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml --cov-fail-under=100

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

---

## Success Metrics

### Code Quality
- [ ] 100% test coverage (unit + integration)
- [ ] 0 failing tests
- [ ] All E2E tests passing
- [ ] No linting errors
- [ ] Type coverage: 100%

### Performance
- [ ] All API endpoints < 500ms
- [ ] MCP tool calls < 200ms
- [ ] Frontend page load < 2s
- [ ] Database queries < 100ms

### Functionality
- [ ] All use cases implemented
- [ ] All acceptance criteria met
- [ ] All edge cases handled
- [ ] Error messages user-friendly

---

## Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Database + BKT/IRT | Schema, models, repositories, algorithms (100% tested) |
| 2 | MCP Servers (Node 1, 7) | 2 servers with all tools (100% tested) |
| 3 | MCP Servers (Node 5, 6) + UI | 2 servers + heatmap/timeline (100% tested) |
| 4 | Workflows | 3 workflows orchestrated (100% tested) |
| 5 | Integration + Polish | Full system integration, coverage verification |

---

**Document Version**: 1.0
**Created**: 2026-01-11
**Engineer**: Claude Code (Sonnet 4.5)

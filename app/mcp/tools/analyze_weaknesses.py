"""
Analyze Student Weaknesses Tool

학생의 약점 개념을 분석하고 숙련도가 낮은 개념을 식별합니다.
"""
from typing import Dict, Any
from app.mcp.tools.base import MCPTool
import logging

logger = logging.getLogger(__name__)


class AnalyzeStudentWeaknessesTool(MCPTool):
    """학생 약점 분석 도구"""

    name: str = "analyze_student_weaknesses"
    description: str = "학생의 약점 개념을 분석하고 숙련도가 낮은 개념을 식별합니다. 주간 진단 워크플로우를 실행하여 추천 문제도 함께 제공합니다."
    category: str = "workflow"
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "학생 ID"
            },
            "curriculum_path": {
                "type": "string",
                "description": "커리큘럼 경로 (예: 중학수학.2학년.1학기)"
            },
            "include_weak_concepts": {
                "type": "boolean",
                "description": "약점 개념 포함 여부",
                "default": True
            }
        },
        "required": ["student_id", "curriculum_path"]
    }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        약점 분석 실행

        Args:
            arguments: student_id, curriculum_path, include_weak_concepts

        Returns:
            {
                "workflow_id": "wf_...",
                "weak_concepts": ["개념1", "개념2"],
                "questions": [...],
                "total_estimated_time_minutes": 30
            }
        """
        from app.services.weekly_diagnostic_service import (
            WeeklyDiagnosticService,
            WeeklyDiagnosticRequest
        )
        from app.mcp.manager import MCPClientManager
        from app.db.session import get_db_context

        logger.info(f"Analyzing weaknesses for student {arguments['student_id']}")

        mcp = MCPClientManager()
        async with get_db_context() as db:
            service = WeeklyDiagnosticService(mcp, db)
            request = WeeklyDiagnosticRequest(
                student_id=arguments["student_id"],
                curriculum_path=arguments["curriculum_path"],
                include_weak_concepts=arguments.get("include_weak_concepts", True)
            )

            result = await service.start_diagnostic(request)

            return {
                "workflow_id": result.workflow_id,
                "session_id": result.session_id,
                "weak_concepts": result.weak_concepts,
                "questions": [
                    {
                        "id": q.id,
                        "content": q.content,
                        "difficulty": q.difficulty,
                        "concepts": q.concepts
                    }
                    for q in result.questions
                ],
                "total_estimated_time_minutes": result.total_estimated_time_minutes,
                "started_at": result.started_at.isoformat()
            }

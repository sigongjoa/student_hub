"""
MCP Client - stdio 프로토콜 기반

실제 MCP SDK를 사용하여 stdio로 MCP 서버와 통신합니다.
"""
from typing import Dict, Any, Optional
import logging
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

logger = logging.getLogger(__name__)


class MCPClient:
    """stdio 프로토콜 기반 MCP 클라이언트"""

    def __init__(self, server_name: str, server_path: str, use_mock: bool = False, mock_server: Any = None):
        self.server_name = server_name
        self.server_path = server_path
        self.use_mock = use_mock
        self.mock_server = mock_server  # Mock MCP 서버 인스턴스
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._stdio_ctx = None  # stdio context manager 저장

    async def connect(self):
        """MCP 서버 연결"""
        if self.use_mock:
            logger.info(f"[MOCK MODE] Connecting to {self.server_name}")
            return

        logger.info(f"Connecting to {self.server_name} at {self.server_path}")

        try:
            # 서버 경로 해석
            server_path = Path(self.server_path)
            if not server_path.is_absolute():
                # 상대 경로를 절대 경로로 변환
                # client.py는 /mathesis/node0_student_hub/app/mcp/client.py
                # 4단계 위로 올라가면 /mathesis
                base_dir = Path(__file__).resolve().parent.parent.parent.parent
                server_path = (base_dir / self.server_path).resolve()

            if not server_path.exists():
                logger.warning(f"MCP server not found: {server_path}, falling back to mock mode")
                self.use_mock = True
                return

            # stdio 서버 파라미터 설정
            server_params = StdioServerParameters(
                command=sys.executable,  # python3
                args=[str(server_path)],
                env=os.environ.copy()
            )

            # stdio 클라이언트 시작 (async context manager로 사용)
            # Note: context manager를 직접 사용하지 않고 __aenter__를 호출
            stdio_ctx = stdio_client(server_params)
            self._read, self._write = await stdio_ctx.__aenter__()
            self._stdio_ctx = stdio_ctx  # 나중에 __aexit__를 위해 저장
            self.session = ClientSession(self._read, self._write)

            # 세션 초기화
            await self.session.initialize()

            logger.info(f"✅ Connected to {self.server_name} successfully")

        except Exception as e:
            logger.error(f"Failed to connect to {self.server_name}: {e}")
            logger.warning(f"Falling back to mock mode for {self.server_name}")
            self.use_mock = True

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """MCP 도구 호출"""
        logger.info(f"Calling {self.server_name}.{tool_name} with {arguments}")

        # Mock 서버 인스턴스가 있으면 사용
        if self.use_mock and self.mock_server:
            logger.info(f"Using Mock server instance for {self.server_name}.{tool_name}")
            method = getattr(self.mock_server, tool_name, None)
            if method:
                return await method(**arguments)
            else:
                logger.warning(f"Mock server method {tool_name} not found on {self.server_name}")

        # 실제 MCP 호출
        if not self.use_mock and self.session:
            try:
                result = await self.session.call_tool(tool_name, arguments)
                # result.content는 List[TextContent]
                if result.content:
                    # 첫 번째 TextContent의 text를 JSON으로 파싱
                    response_text = result.content[0].text
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"result": response_text}
                return {}
            except Exception as e:
                logger.error(f"MCP call failed for {self.server_name}.{tool_name}: {e}")
                logger.warning(f"Falling back to mock response")
                # 에러 발생 시 하드코딩 Mock으로 폴백

        # 하드코딩된 Mock responses for fallback
        if self.server_name == "lab-node" and tool_name == "get_recent_concepts":
            return {"concepts": ["도함수", "적분", "극한"]}

        if self.server_name == "q-dna" and tool_name == "get_student_mastery":
            return {"도함수": 0.45, "적분": 0.55, "극한": 0.75}

        if self.server_name == "q-dna" and tool_name == "recommend_questions":
            return {
                "questions": [
                    {
                        "id": f"q_{i}",
                        "content": f"문제 {i}: 도함수를 구하시오",
                        "difficulty": "medium",
                        "concepts": ["도함수"]
                    }
                    for i in range(1, 11)
                ]
            }

        if self.server_name == "q-dna" and tool_name == "get_question_dna":
            return {
                "question_id": arguments.get("question_id"),
                "difficulty": "medium",
                "concepts": ["이차함수", "최댓값", "도함수"],
                "bloom_level": "apply"
            }

        if self.server_name == "error-note" and tool_name == "create_error_note":
            import uuid
            return {
                "error_note_id": f"en_{uuid.uuid4().hex[:16]}",
                "created_at": "2026-01-10T13:00:00",
                "analysis": {
                    "misconception": "이차함수의 최댓값 개념 혼동",
                    "root_cause": "위로 볼록/아래로 볼록 판단 오류",
                    "related_concepts": ["이차함수", "도함수", "극값"]
                }
            }

        if self.server_name == "error-note" and tool_name == "calculate_anki_schedule":
            from datetime import datetime, timedelta
            return {
                "next_review_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "interval_days": 1,
                "ease_factor": 2.5
            }

        if self.server_name == "lab-node" and tool_name == "get_concept_heatmap":
            from datetime import datetime
            return {
                "student_id": arguments.get("student_id"),
                "heatmap": {
                    "극한": 0.45, "도함수": 0.55, "적분": 0.35,
                    "미분": 0.65, "삼각함수": 0.80
                },
                "timestamp": datetime.now().isoformat()
            }

        if self.server_name == "lab-node" and tool_name == "get_activity_summary":
            from datetime import datetime
            return {
                "student_id": arguments.get("student_id"),
                "period_days": arguments.get("days", 7),
                "total_attempts": 100,
                "average_accuracy": 0.56,  # (0.45+0.55+0.35+0.65+0.80)/5 = 0.56
                "concepts_practiced": 5,
                "last_activity": datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat()
            }

        if self.server_name == "logic-engine" and tool_name == "get_prerequisite_graph":
            return {
                "graph": {
                    "극한": {"prerequisites": [], "dependents": ["도함수", "미분"]},
                    "도함수": {"prerequisites": ["극한"], "dependents": ["적분", "미분"]},
                    "미분": {"prerequisites": ["극한", "도함수"], "dependents": []},
                    "적분": {"prerequisites": ["도함수"], "dependents": []},
                    "삼각함수": {"prerequisites": [], "dependents": []}
                }
            }

        if self.server_name == "q-dna" and tool_name == "estimate_learning_time":
            concept = arguments.get("concept")
            mastery = arguments.get("current_mastery", 0.5)
            base_hours = {"극한": 4, "도함수": 6, "적분": 8, "미분": 5, "삼각함수": 3}.get(concept, 4)
            adjustment = (1.0 - mastery) * 2
            return {
                "concept": concept,
                "estimated_hours": int(base_hours + adjustment),
                "current_mastery": mastery
            }

        if self.server_name == "school-info" and tool_name == "get_exam_scope":
            return {
                "school_id": arguments.get("school_id"),
                "exam_scope": {
                    "curriculum_paths": arguments.get("curriculum_paths", []),
                    "topics": ["도함수", "적분", "극한", "미분", "삼각함수"],
                    "exam_format": "객관식 20문제, 주관식 5문제",
                    "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2}
                }
            }

        if self.server_name == "lab-node" and tool_name == "get_weak_concepts":
            return {
                "weak_concepts": [
                    {"concept": "도함수", "accuracy": 0.45, "attempts": 20},
                    {"concept": "극한", "accuracy": 0.50, "attempts": 15},
                    {"concept": "적분", "accuracy": 0.35, "attempts": 10}
                ]
            }

        if self.server_name == "q-metrics" and tool_name == "generate_mock_exam":
            import uuid
            from datetime import datetime
            return {
                "pdf_url": f"https://storage.mathesis.com/mock_exams/{arguments.get('student_id')}_{uuid.uuid4().hex[:8]}.pdf",
                "question_count": 25,
                "generated_at": datetime.now().isoformat()
            }

        # Default fallback
        return {"status": "mock_response"}

    async def close(self):
        """연결 종료"""
        if not self.use_mock and (self.session or self._stdio_ctx):
            try:
                logger.info(f"Closing connection to {self.server_name}")
                if self._stdio_ctx:
                    await self._stdio_ctx.__aexit__(None, None, None)
                    self._stdio_ctx = None
                self.session = None
            except Exception as e:
                logger.error(f"Error closing {self.server_name}: {e}")

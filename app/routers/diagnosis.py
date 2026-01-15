"""
인지 진단 라우터 (Node0 - Master Hub)

Node4 → Node0 → Node2 이벤트 기반 통신
- Node4에서 진단 요청 수신
- 이벤트 로그 기록 및 브로드캐스트
- Node2 (Q-DNA) API로 진단 요청 중계
- 결과를 Node4에 반환
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
import asyncio
import logging
from collections import deque

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagnosis", tags=["Cognitive Diagnosis"])

# ============== Event Log Storage ==============
# In-memory event log (실제 환경에서는 Redis/DB 사용)
diagnosis_events: deque = deque(maxlen=100)
event_subscribers: List[asyncio.Queue] = []

# Node2 (Q-DNA) API URL
NODE2_API_URL = "http://localhost:8002/api/v1"


# ============== Event Models ==============

class DiagnosisEvent(BaseModel):
    """진단 이벤트 로그"""
    event_id: str
    event_type: str  # request, processing, response, error
    timestamp: str
    source: str  # node4, node0, node2
    target: str
    student_id: str
    data: Dict[str, Any]
    message: str


# ============== Request/Response Models ==============

class DiagnoseRequest(BaseModel):
    """진단 요청 (Node4 → Node0)"""
    student_id: str = Field(..., description="학생 ID")
    question_content: str = Field(..., description="문제 내용")
    student_answer: str = Field(..., description="학생 답안")
    correct_answer: Optional[str] = Field(None, description="정답")
    question_id: Optional[str] = Field(None, description="문제 ID")
    subject: str = Field(default="수학", description="과목명")


class DiagnosisResponse(BaseModel):
    """진단 결과 (Node0 → Node4)"""
    student_id: str
    question_id: Optional[str]
    is_correct: bool
    error_type: Optional[str]
    reasoning_trace: str
    error_location: Optional[str]
    feedback: str
    recommendation: str
    concepts_involved: List[str]
    kg_operations: List[Dict[str, Any]]
    confidence: float
    timestamp: str
    # Event tracking
    event_id: str
    processed_by: str = "node2"


# ============== Helper Functions ==============

def create_event(
    event_type: str,
    source: str,
    target: str,
    student_id: str,
    data: Dict[str, Any],
    message: str
) -> DiagnosisEvent:
    """이벤트 생성"""
    import uuid
    event = DiagnosisEvent(
        event_id=str(uuid.uuid4())[:8],
        event_type=event_type,
        timestamp=datetime.now().isoformat(),
        source=source,
        target=target,
        student_id=student_id,
        data=data,
        message=message
    )
    diagnosis_events.append(event.model_dump())

    # Broadcast to subscribers
    for queue in event_subscribers:
        try:
            queue.put_nowait(event.model_dump())
        except asyncio.QueueFull:
            pass

    logger.info(f"[EVENT] {event_type}: {source} → {target} | {message}")
    return event


async def call_node2_diagnosis(request: DiagnoseRequest) -> Dict[str, Any]:
    """Node2 (Q-DNA) API 호출"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{NODE2_API_URL}/diagnosis/analyze",
            json={
                "student_id": request.student_id,
                "question_content": request.question_content,
                "student_answer": request.student_answer,
                "correct_answer": request.correct_answer,
                "question_id": request.question_id,
                "subject": request.subject
            }
        )
        response.raise_for_status()
        return response.json()


# ============== API Endpoints ==============

@router.post("/analyze", response_model=DiagnosisResponse)
async def analyze_student_answer(request: DiagnoseRequest):
    """
    학생 답안 인지 진단 (Node4 → Node0 → Node2)

    1. Node4에서 요청 수신
    2. 이벤트 로그 기록
    3. Node2로 진단 요청 중계
    4. 결과 반환 및 이벤트 로그
    """
    import uuid
    event_id = str(uuid.uuid4())[:8]

    # 1. 요청 수신 이벤트
    create_event(
        event_type="request",
        source="node4",
        target="node0",
        student_id=request.student_id,
        data={"question": request.question_content[:50] + "..."},
        message=f"진단 요청 수신 - 학생: {request.student_id}"
    )

    # 2. Node2로 중계 이벤트
    create_event(
        event_type="processing",
        source="node0",
        target="node2",
        student_id=request.student_id,
        data={"event_id": event_id},
        message="Node2 (Q-DNA) 인지 진단 서비스로 요청 전달"
    )

    try:
        # 3. Node2 API 호출
        result = await call_node2_diagnosis(request)

        # 4. 응답 수신 이벤트
        create_event(
            event_type="response",
            source="node2",
            target="node0",
            student_id=request.student_id,
            data={
                "is_correct": result.get("is_correct"),
                "error_type": result.get("error_type"),
                "confidence": result.get("confidence")
            },
            message=f"진단 완료 - {'정답' if result.get('is_correct') else '오답'} (신뢰도: {result.get('confidence', 0):.0%})"
        )

        # 5. Node4로 응답 이벤트
        create_event(
            event_type="response",
            source="node0",
            target="node4",
            student_id=request.student_id,
            data={"event_id": event_id},
            message="진단 결과 Node4로 전송"
        )

        return DiagnosisResponse(
            **result,
            event_id=event_id,
            processed_by="node2"
        )

    except httpx.HTTPStatusError as e:
        create_event(
            event_type="error",
            source="node2",
            target="node0",
            student_id=request.student_id,
            data={"error": str(e)},
            message=f"Node2 오류: {e.response.status_code}"
        )
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

    except httpx.ConnectError:
        # Node2 연결 실패 시 Fallback
        create_event(
            event_type="error",
            source="node0",
            target="node2",
            student_id=request.student_id,
            data={},
            message="Node2 연결 실패 - Mock 응답 생성"
        )

        # Mock 응답
        mock_result = {
            "student_id": request.student_id,
            "question_id": request.question_id,
            "is_correct": False,
            "error_type": "knowledge_gap",
            "reasoning_trace": "[Mock] Node2 연결 실패로 Mock 응답 생성",
            "error_location": None,
            "feedback": "현재 진단 서비스에 연결할 수 없습니다.",
            "recommendation": "잠시 후 다시 시도해주세요.",
            "concepts_involved": [],
            "kg_operations": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }

        return DiagnosisResponse(
            **mock_result,
            event_id=event_id,
            processed_by="mock"
        )


@router.get("/events")
async def get_recent_events(limit: int = 20):
    """최근 진단 이벤트 조회"""
    events = list(diagnosis_events)[-limit:]
    return {"events": events, "total": len(diagnosis_events)}


@router.get("/events/stream")
async def stream_events():
    """
    이벤트 스트림 (Server-Sent Events)

    프론트엔드에서 실시간으로 이벤트를 수신할 수 있음
    """
    from fastapi.responses import StreamingResponse

    queue = asyncio.Queue(maxsize=50)
    event_subscribers.append(queue)

    async def event_generator():
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {str(event)}\n\n"
        except asyncio.TimeoutError:
            yield f"data: {{'type': 'keepalive'}}\n\n"
        finally:
            event_subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/profile/{student_id}")
async def get_student_profile(student_id: str):
    """
    학생 지식 프로필 조회 (Node2 → Node0 → Node4)
    """
    create_event(
        event_type="request",
        source="node4",
        target="node0",
        student_id=student_id,
        data={},
        message=f"학생 프로필 요청 - {student_id}"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{NODE2_API_URL}/diagnosis/profile/{student_id}")
            response.raise_for_status()

            create_event(
                event_type="response",
                source="node2",
                target="node0",
                student_id=student_id,
                data={},
                message="학생 프로필 수신 완료"
            )

            return response.json()

    except httpx.ConnectError:
        create_event(
            event_type="error",
            source="node0",
            target="node2",
            student_id=student_id,
            data={},
            message="Node2 연결 실패"
        )
        raise HTTPException(status_code=503, detail="Node2 service unavailable")


@router.get("/health")
async def health_check():
    """진단 서비스 상태 확인"""
    node2_status = "unknown"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{NODE2_API_URL}/diagnosis/health")
            if response.status_code == 200:
                node2_status = "connected"
    except:
        node2_status = "disconnected"

    return {
        "status": "healthy",
        "node0": "running",
        "node2": node2_status,
        "events_count": len(diagnosis_events),
        "subscribers": len(event_subscribers)
    }

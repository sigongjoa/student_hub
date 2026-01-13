"""
Chat API Router

대화형 채팅 엔드포인트 (SSE Streaming)
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid
import json
import logging

from app.db.session import get_db
from app.agents import AgentOrchestrator
from app.models.conversation import Conversation, Message
from app.mcp.tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Global orchestrator (싱글톤) - llama3:latest 사용
orchestrator = AgentOrchestrator(model_name="llama3:latest")

# Register MCP tools
for name, tool in TOOL_REGISTRY.items():
    orchestrator.register_tool({
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.input_schema
    })


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True


class ChatResponse(BaseModel):
    message: str
    session_id: str
    metadata: Optional[dict] = None


@router.post("/")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    대화형 채팅 엔드포인트

    Args:
        request: ChatRequest (message, session_id, stream)
        db: Database session

    Returns:
        StreamingResponse (SSE) or ChatResponse
    """
    # Session ID 생성 (없으면)
    session_id = request.session_id or str(uuid.uuid4())

    logger.info(f"Chat request: session={session_id}, message={request.message[:50]}...")

    # Streaming 응답
    if request.stream:
        async def generate():
            try:
                async for chunk in orchestrator.chat(
                    user_message=request.message,
                    session_id=session_id,
                    stream=True
                ):
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

                # 종료 신호
                yield f"data: {json.dumps({'done': True, 'session_id': session_id}, ensure_ascii=False)}\n\n"

            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    # Non-streaming 응답
    else:
        try:
            response_text = ""
            async for chunk in orchestrator.chat(
                user_message=request.message,
                session_id=session_id,
                stream=False
            ):
                response_text += chunk

            return ChatResponse(
                message=response_text,
                session_id=session_id
            )

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    대화 히스토리 조회

    Args:
        session_id: 세션 ID
        db: Database session

    Returns:
        대화 히스토리
    """
    try:
        # DB에서 조회
        conversation = await db.get(Conversation, session_id)
        if not conversation:
            return {
                "session_id": session_id,
                "messages": []
            }

        return {
            "session_id": session_id,
            "title": conversation.title,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.message_metadata
                }
                for msg in conversation.messages
            ]
        }

    except Exception as e:
        logger.error(f"Get history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def delete_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    대화 히스토리 삭제

    Args:
        session_id: 세션 ID
        db: Database session

    Returns:
        성공 메시지
    """
    try:
        # DB에서 삭제
        conversation = await db.get(Conversation, session_id)
        if conversation:
            await db.delete(conversation)
            await db.commit()

        # Memory에서 삭제
        orchestrator.clear_history(session_id)

        return {"success": True, "message": f"Session {session_id} deleted"}

    except Exception as e:
        logger.error(f"Delete history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_ollama():
    """
    Ollama 연결 테스트

    Returns:
        Ollama 상태
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            response.raise_for_status()
            data = response.json()

            models = [model["name"] for model in data.get("models", [])]

            return {
                "status": "connected",
                "models": models,
                "current_model": orchestrator.model_name
            }

    except Exception as e:
        logger.error(f"Ollama test error: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "message": "Ollama가 실행되지 않았거나 연결할 수 없습니다. 'ollama serve'를 실행하세요."
        }

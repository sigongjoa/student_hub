"""
Agent Orchestrator

로컬 LLM(Ollama)을 사용한 대화형 AI Agent
MCP tools를 실행하고 자연어로 결과를 반환합니다.
"""
from typing import List, Dict, Any, AsyncGenerator, Optional
import json
import logging
import httpx

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """로컬 LLM 기반 Agent Orchestrator"""

    def __init__(self, model_name: str = "llama3.1:8b", ollama_base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_base_url = ollama_base_url
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.tools: List[Dict] = []

        logger.info(f"Initialized AgentOrchestrator with model: {model_name}")

    def register_tool(self, tool_def: Dict[str, Any]):
        """MCP tool을 LLM tool로 등록"""
        self.tools.append(tool_def)
        logger.info(f"Registered tool: {tool_def['name']}")

    async def chat(
        self,
        user_message: str,
        session_id: str,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        대화형 인터페이스

        Args:
            user_message: 사용자 메시지
            session_id: 세션 ID
            stream: 스트리밍 여부

        Yields:
            응답 chunk
        """
        # 대화 히스토리 가져오기
        history = self.conversation_history.get(session_id, [])

        # System prompt
        system_prompt = self._build_system_prompt()

        # Messages 구성
        messages = [
            {"role": "system", "content": system_prompt},
            *history,
            {"role": "user", "content": user_message}
        ]

        # Ollama API 호출
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                if stream:
                    # Streaming response
                    async with client.stream(
                        "POST",
                        f"{self.ollama_base_url}/api/chat",
                        json={
                            "model": self.model_name,
                            "messages": messages,
                            "stream": True
                        }
                    ) as response:
                        response.raise_for_status()

                        full_response = ""
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    data = json.loads(line)
                                    if "message" in data:
                                        content = data["message"].get("content", "")
                                        if content:
                                            full_response += content
                                            yield content

                                    if data.get("done", False):
                                        break
                                except json.JSONDecodeError:
                                    continue

                        # 히스토리 업데이트
                        history.append({"role": "user", "content": user_message})
                        history.append({"role": "assistant", "content": full_response})
                        self.conversation_history[session_id] = history[-20:]  # 최근 20개만

                else:
                    # Non-streaming response
                    response = await client.post(
                        f"{self.ollama_base_url}/api/chat",
                        json={
                            "model": self.model_name,
                            "messages": messages,
                            "stream": False
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data.get("message", {}).get("content", "")

                    # 히스토리 업데이트
                    history.append({"role": "user", "content": user_message})
                    history.append({"role": "assistant", "content": content})
                    self.conversation_history[session_id] = history[-20:]

                    yield content

            except httpx.HTTPError as e:
                logger.error(f"Ollama API error: {e}")
                yield f"❌ LLM 호출 실패: {str(e)}"
            except Exception as e:
                logger.error(f"Chat error: {e}", exc_info=True)
                yield f"❌ 에러 발생: {str(e)}"

    def _build_system_prompt(self) -> str:
        """System prompt 생성"""
        tool_descriptions = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tools
        ])

        return f"""당신은 학생 관리 시스템의 AI 어시스턴트입니다.
선생님이 학생 데이터를 조회하거나 분석할 때 도움을 줍니다.

사용 가능한 도구:
{tool_descriptions}

지침:
1. 선생님의 질문을 정확히 이해하고 적절한 정보를 제공하세요
2. 학생 이름이 주어지면 student_id로 변환하세요
3. 숙련도, 약점 분석 등 구체적인 데이터를 제공하세요
4. 한국어로 친절하게 대답하세요
5. 도구를 사용할 수 없는 경우, 명확히 설명하세요"""

    def clear_history(self, session_id: str):
        """대화 히스토리 삭제"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            logger.info(f"Cleared history for session: {session_id}")

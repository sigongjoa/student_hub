"""
Base MCP Tool Class

모든 MCP tool의 추상 기본 클래스
"""
from typing import Dict, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class MCPTool(ABC, BaseModel):
    """MCP Tool 추상 기본 클래스"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = "general"

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool 실행

        Args:
            arguments: Tool 실행에 필요한 인자들

        Returns:
            실행 결과 (JSON serializable dict)

        Raises:
            ValueError: 인자 검증 실패
            Exception: 실행 중 에러
        """
        raise NotImplementedError

    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """
        인자 검증

        Args:
            arguments: 검증할 인자들

        Raises:
            ValueError: 필수 인자 누락 또는 타입 불일치
        """
        # Check required fields
        required = self.input_schema.get("required", [])
        for field in required:
            if field not in arguments:
                raise ValueError(f"Missing required argument: {field}")

        # Type validation can be added here
        properties = self.input_schema.get("properties", {})
        for field, value in arguments.items():
            if field in properties:
                expected_type = properties[field].get("type")
                # Basic type checking
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Argument '{field}' must be a string")
                elif expected_type == "integer" and not isinstance(value, int):
                    raise ValueError(f"Argument '{field}' must be an integer")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Argument '{field}' must be a boolean")

    async def safe_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        안전한 실행 (에러 처리 포함)

        Args:
            arguments: Tool 실행 인자

        Returns:
            실행 결과 또는 에러 정보
        """
        try:
            self.validate_arguments(arguments)
            result = await self.execute(arguments)
            return {
                "success": True,
                "result": result
            }
        except ValueError as e:
            logger.error(f"Validation error in {self.name}: {e}")
            return {
                "success": False,
                "error": f"Validation error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Execution error in {self.name}: {e}")
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }

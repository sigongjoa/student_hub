from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Node 0 설정"""

    # API Server
    API_PORT: int = 8000  # FastAPI 서버 포트 (Chat API)

    # gRPC Server
    GRPC_PORT: int = 50050  # Node 0 전용 포트 (기존 서비스)
    GRPC_MCP_PORT: int = 50051  # Node 0 MCP 서버 포트 (새로운 대화형 시스템)
    GRPC_MAX_WORKERS: int = 10

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "student_hub"
    POSTGRES_USER: str = "mathesis"
    POSTGRES_PASSWORD: str = "password"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"{self.DATABASE_URL}_test"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # MCP Server Paths (상대 경로는 mathesis/ 기준)
    NODE2_MCP_PATH: str = "node2_q_dna/backend/mcp_server.py"
    NODE4_MCP_PATH: str = "node4_lab_node/backend/mcp_server.py"
    NODE7_MCP_PATH: str = "node7_error_note/backend/mcp_server.py"
    NODE1_MCP_PATH: str = "node1_logic_engine/backend/mcp_server.py"
    NODE5_MCP_PATH: str = "node5_q_metrics/backend/mcp_server.py"
    NODE6_MCP_PATH: str = "node6_school_info/mcp_server.py"

    # MCP Configuration
    USE_MOCK_MCP: bool = True  # False = 실제 MCP 사용, True = Mock 사용 (stdio hang issue)

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()

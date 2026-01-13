"""
Custom Tool Model

사용자가 정의한 커스텀 MCP tool
"""
from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class CustomTool(Base):
    """커스텀 Tool 모델"""
    __tablename__ = "custom_tools"

    id = Column(String, primary_key=True, default=lambda: f"ct_{uuid.uuid4().hex[:16]}")
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    input_schema = Column(Text, nullable=False)  # JSON schema as string
    definition = Column(JSON, nullable=False)  # CustomToolDefinition
    created_by = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)

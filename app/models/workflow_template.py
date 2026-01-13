"""
Workflow Template Model

워크플로우 템플릿 정의
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, Text
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class WorkflowTemplate(Base):
    """워크플로우 템플릿 모델"""
    __tablename__ = "workflow_templates"

    id = Column(String, primary_key=True, default=lambda: f"wft_{uuid.uuid4().hex[:16]}")
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    definition = Column(JSON, nullable=False)  # WorkflowTemplate schema
    created_by = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_public = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)

    # Execution statistics
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)

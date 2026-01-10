from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class WorkflowSession(Base):
    """워크플로우 실행 세션 추적"""
    __tablename__ = "workflow_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, unique=True, default=lambda: f"wf_{uuid.uuid4().hex[:16]}")
    student_id = Column(String, nullable=False)
    workflow_type = Column(String(50), nullable=False)  # weekly_diagnostic, error_review, etc.
    status = Column(String(20), default="in_progress")  # in_progress, completed, failed
    metadata = Column(JSON, default=dict)  # 워크플로우별 커스텀 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

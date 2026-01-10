from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


class Student(Base):
    """학생 모델"""
    __tablename__ = "students"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: f"student_{uuid.uuid4().hex[:12]}")
    name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False)
    school_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

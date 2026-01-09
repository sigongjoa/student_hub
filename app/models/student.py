from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from node0_student_hub.app.db.base import Base
import uuid
from datetime import datetime

class Student(Base):
    """
    학생 마스터 데이터 엔티티
    """
    __tablename__ = "students"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    name = Column(String(100), nullable=False, comment="학생 이름")
    school_id = Column(String(50), nullable=False, index=True)
    grade = Column(Integer, nullable=False)
    class_name = Column(String(50), nullable=True)
    student_number = Column(String(20), nullable=True)

    # Contact
    email = Column(String(255), nullable=True)
    parent_contact = Column(String(20), nullable=True)

    # Metadata (JSONB)
    metadata_ = Column("metadata", JSON, default={}, nullable=False)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")
    learning_history = relationship("LearningHistory", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name})>"

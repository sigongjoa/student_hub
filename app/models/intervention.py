from sqlalchemy import Column, String, TIMESTAMP, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from node0_student_hub.app.db.base import Base
from datetime import datetime
import uuid

class Intervention(Base):
    """
    학습 개입 엔티티
    """
    __tablename__ = "interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(String(50), nullable=False)
    weak_areas = Column(JSON, nullable=False)
    learning_path = Column(JSON, nullable=False)

    status = Column(String(20), nullable=False, default="active", index=True)
    progress = Column(JSON, default={"completed": 0, "total": 0}, nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(TIMESTAMP, nullable=True)

    student = relationship("Student", back_populates="interventions")

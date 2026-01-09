from sqlalchemy import Column, String, Integer, TIMESTAMP, JSON, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from node0_student_hub.app.db.base import Base
from datetime import datetime

class LearningHistory(Base):
    """
    학습 이벤트 엔티티
    """
    __tablename__ = "learning_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    occurred_at = Column(TIMESTAMP, primary_key=True, nullable=False, index=True) # Partition key

    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)

    event_type = Column(String(50), nullable=False, index=True)
    source_node = Column(Integer, nullable=False)
    source_id = Column(String(255), nullable=True)

    content = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    student = relationship("Student", back_populates="learning_history")

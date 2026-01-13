"""
StudentAttempt Model

학생의 문제 풀이 시도 기록을 저장하는 모델입니다.
각 시도는 정답 여부, 응답 시간, 개념 등을 포함합니다.

이 데이터는 BKT 알고리즘을 통한 숙련도 계산의 기초가 됩니다.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from app.db.base import Base


class StudentAttempt(Base):
    """
    학생 문제 풀이 시도 모델

    Attributes:
        id: 시도 고유 ID (자동 생성)
        student_id: 학생 ID (외래키)
        question_id: 문제 ID
        concept: 학습 개념 (예: "도함수", "적분")
        is_correct: 정답 여부
        response_time_ms: 응답 시간 (밀리초)
        attempted_at: 시도 시각 (UTC)
    """
    __tablename__ = "student_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(100), nullable=False, index=True)
    question_id = Column(String(100), nullable=False)
    concept = Column(String(100), nullable=False, index=True)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    attempted_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    # 복합 인덱스: 학생별, 개념별 쿼리 최적화
    __table_args__ = (
        Index('idx_student_concept', 'student_id', 'concept'),
        Index('idx_student_date', 'student_id', 'attempted_at'),
    )

    def __repr__(self) -> str:
        """문자열 표현"""
        return (
            f"<StudentAttempt(id={self.id}, "
            f"student_id='{self.student_id}', "
            f"question_id='{self.question_id}', "
            f"concept='{self.concept}', "
            f"is_correct={self.is_correct})>"
        )

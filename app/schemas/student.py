from pydantic import BaseModel, Field, EmailStr, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime

class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    school_id: str = Field(..., min_length=1, max_length=50)
    grade: int = Field(..., ge=1, le=12)
    class_name: Optional[str] = Field(None, max_length=50)
    student_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    parent_contact: Optional[str] = Field(None, max_length=20)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    parent_contact: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class StudentResponse(StudentBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UnifiedProfile(BaseModel):
    student_id: UUID4
    basic_info: Dict[str, Any]
    knowledge_state: Optional[Dict[str, Any]] = None
    mastery_levels: Optional[Dict[str, Any]] = None
    recent_activities: Optional[List[Dict[str, Any]]] = None
    latest_reports: Optional[List[Dict[str, Any]]] = None
    cached: bool = False
    generated_at: datetime = Field(default_factory=datetime.now)

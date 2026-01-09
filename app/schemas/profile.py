from pydantic import BaseModel, Field
from typing import Optional, List

class GetUnifiedProfileInput(BaseModel):
    student_id: str
    include_sections: List[str] = Field(default_factory=list)
    time_range: str = "last_30_days"
    include_history: bool = False
    days: int = 30

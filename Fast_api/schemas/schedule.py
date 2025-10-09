from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ScheduleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_at: datetime

class ScheduleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    is_completed: Optional[bool] = None

class ScheduleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    scheduled_at: datetime
    is_completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NaturalLanguageInput(BaseModel):
    text: str = Field(..., min_length=1)

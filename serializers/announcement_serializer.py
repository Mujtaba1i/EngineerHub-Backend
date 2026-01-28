from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnnouncementSchema(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    event_date: datetime
    class_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreateAnnouncementSchema(BaseModel):
    title: str
    content: str
    event_date: datetime
    class_id: int

    class Config:
        from_attributes = True

class UpdateAnnouncementSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    event_date: Optional[datetime] = None

    class Config:
        from_attributes = True
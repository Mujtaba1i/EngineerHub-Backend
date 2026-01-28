from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteSchema(BaseModel):
    id: Optional[int] = None
    title: str
    file_name: str
    file_key: str
    file_type: str
    file_size: Optional[int] = None
    course_code: str
    course_name: Optional[str] = None
    year: int
    doctor_name: str
    description: Optional[str] = None
    uploader_id: int
    likes_count: int = 0
    dislikes_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # User's like status (if authenticated)
    user_like_status: Optional[int] = None  # 1 for liked, -1 for disliked, None for no action
    download_url: Optional[str] = None  # Presigned URL for download

    class Config:
        from_attributes = True


class CreateNoteSchema(BaseModel):
    title: str
    course_code: str
    course_name: Optional[str] = None
    year: int
    doctor_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateNoteSchema(BaseModel):
    title: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    year: Optional[int] = None
    doctor_name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class NoteLikeSchema(BaseModel):
    note_id: int
    is_like: int

    class Config:
        from_attributes = True
from pydantic import BaseModel
from typing import Optional


class GraduateProjectCreateSchema(BaseModel):
    title: str
    summary: str
    major: str
    graduation_year: int

    poster: str
    contact_email: str
    contact_phone: Optional[str] = None
    linkedin: Optional[str] = None
    poster: Optional[str] = None

    class Config:
        from_attributes = True


class GraduateProjectSchema(BaseModel):
    id: Optional[int] = None

    title: str
    summary: str
    major: str
    graduation_year: int

    poster: str
    contact_email: str
    contact_phone: Optional[str] = None
    linkedin: Optional[str] = None
    poster: Optional[str] = None

    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class GraduateProjectUpdateSchema(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None

    poster: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    linkedin: Optional[str] = None
    poster: Optional[str] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from .user import UserSchema

class ClassSchema(BaseModel):
    id: Optional[int] = None
    name: str
    doctor_id: int
    doctor_role: Optional[dict] = None
    enrollments: List[dict] = []

    class Config:
        orm_mode = True

class CreateClassSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True

class UpdateClassSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True

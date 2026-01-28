from pydantic import BaseModel
from typing import Optional, List
from .role import RoleSchema
from .student_class import StudentClassSchema
from .user import UserSchema

class ClassSchema(BaseModel):
    id: Optional[int] = None
    name: str
    doctor_id: int
    doctor: Optional[UserSchema] = None
    enrollments: List[StudentClassSchema] = []

    class Config:
        from_attributes = True

class CreateClassSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True

class UpdateClassSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True

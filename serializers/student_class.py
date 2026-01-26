from pydantic import BaseModel
from typing import Optional
from .user import UserSchema

class StudentClassSchema(BaseModel):
    id: Optional[int] = None
    class_id: int
    student: Optional[UserSchema] = None

    class Config:
        orm_mode = True

class CreateStudentClassSchema(BaseModel):
    student_id: int
    class_id: int

    class Config:
        orm_mode = True

class UpdateStudentClassSchema(BaseModel):
    student_id: int
    class_id: int

    class Config:
        orm_mode = True

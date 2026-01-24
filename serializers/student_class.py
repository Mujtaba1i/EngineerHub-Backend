from pydantic import BaseModel
from typing import Optional

class StudentClassSchema(BaseModel):
    id: Optional[int] = None
    student_id: int
    class_id: int
    student: Optional[dict] = None
    class_: Optional[dict] = None

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

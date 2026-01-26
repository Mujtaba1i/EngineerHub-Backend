from pydantic import BaseModel
from typing import Optional, List
from .class_serializer import ClassSchema

class EnrollmentSchema(BaseModel):
    id: int
    class_: ClassSchema
    student_id: int
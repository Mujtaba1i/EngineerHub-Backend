from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from .student_class import StudentClassModel

class ClassModel(BaseModel):

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    doctor = relationship("UserModel", back_populates="classes", passive_deletes=True)
    enrollments = relationship("StudentClassModel",back_populates="class_",cascade="all, delete-orphan",passive_deletes=True)

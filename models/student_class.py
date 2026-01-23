from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class StudentClassModel(BaseModel):

    __tablename__ = "students_classes"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)

    student = relationship("UserModel", back_populates="enrollments", passive_deletes=True)
    class_ = relationship("ClassModel", back_populates="enrollments", passive_deletes=True)

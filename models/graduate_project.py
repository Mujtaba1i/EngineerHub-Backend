from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class GraduateProjectModel(BaseModel):
    __tablename__ = "graduate_projects"

    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    poster = Column(String, nullable=True) 
    major = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=False)

    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="projects")

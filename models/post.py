from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import BaseModel 

class PostModel(BaseModel):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    institute_id = Column(Integer, ForeignKey("users.id"))  


    institute = relationship("UserModel", back_populates="posts") 

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from .user import UserModel
from .classes import ClassModel


class RoleModel(BaseModel):

    __tablename__ = "roles"

    # Required 
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Role Related
    major = Column(String, nullable=True)
    department = Column(String, nullable=True)
    approval = Column(Boolean, nullable=True)

    user = relationship("UserModel", back_populates="user_roles", foreign_keys=[user_id])
    classes = relationship("ClassModel", back_populates="doctor_role", cascade="all, delete-orphan")

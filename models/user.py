from datetime import datetime, timedelta, timezone
from enum import Enum as PyEnum
from passlib.context import CryptContext
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from config.environment import secret
from .base import BaseModel
from .graduate_project import GraduateProjectModel
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(PyEnum):
    STUDENT = "student"
    GRADUATE = "graduate"
    DOCTOR = "doctor"
    INSTITUTION = "institution"


class UserModel(BaseModel):
    __tablename__ = "users"

    # Required
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="user_role_enum", create_constraint=True),nullable=False)

    # Depends on the role
    major = Column(String, nullable=True)
    uni_id = Column(Integer, nullable=True, unique=True, index=True)
    department = Column(String, nullable=True)
    phone_num = Column(String, nullable=True, unique= True)
    office_num = Column(String, nullable=True, unique= True)
    license = Column(String, nullable=True)

    # Relationships
    enrollments = relationship("StudentClassModel", back_populates="student", cascade="all, delete-orphan")
    classes = relationship("ClassModel", back_populates="doctor", cascade="all, delete-orphan")
    projects = relationship("GraduateProjectModel", back_populates="user" , cascade="all, delete-orphan")
    posts = relationship("PostModel", back_populates="institute", cascade="all, delete-orphan")


    def set_password(self, password: str) -> None:
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, str(self.password))

    def generate_token(self) -> str:
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
            "iat": datetime.now(timezone.utc),
            "sub": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "major": self.major,
        }

        token = jwt.encode(payload, secret, algorithm="HS256")
        return token
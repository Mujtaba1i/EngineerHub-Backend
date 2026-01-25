from pydantic import BaseModel
from typing import Optional

class UserRegistrationSchema(BaseModel):
    name: str
    email: str
    password: str
    role: str

    department: Optional[str] = None
    phone_num: Optional[int] = None
    office_num: Optional[int] = None
    uni_id: Optional[int] = None
    major: Optional[str] = None
    license: Optional[str] = None
    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    role: str
    major: Optional[str] = None
    uni_id: Optional[int] = None
    department: Optional[str] = None
    phone_num: Optional[str] = None
    office_num: Optional[str] = None
    license: Optional[str] = None

    class Config:
        orm_mode = True

class UserTokenSchema(BaseModel):
    token: str
    
    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    email: Optional[str] = None
    uni_id: Optional[int]=None
    password: str
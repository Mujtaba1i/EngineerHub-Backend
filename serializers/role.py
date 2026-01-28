from pydantic import BaseModel
from typing import Optional

class RoleSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    major: Optional[str] = None
    department: Optional[str] = None
    approval: Optional[bool] = None

    class Config:
        from_attributes = True

class CreateRoleSchema(BaseModel):
    user_id: int
    major: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True

class UpdateRoleSchema(BaseModel):
    major: Optional[str] = None
    department: Optional[str] = None
    approval: Optional[bool] = None

    class Config:
        from_attributes = True

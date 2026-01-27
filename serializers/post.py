from pydantic import BaseModel
from typing import Optional


class PostCreateSchema(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class PostUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class PostSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    image_url: Optional[str] = None
    institute_id: int

    class Config:
        orm_mode = True

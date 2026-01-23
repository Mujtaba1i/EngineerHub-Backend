from pydantic import BaseModel
from .user import UserSchema

class CommentSchema(BaseModel):
  id: int
  content: str
  user: UserSchema

  class Config:
    orm_mode = True

class CreateCommentSchema(BaseModel):
  content: str

class UpdateCommentSchema(BaseModel):
  content: str

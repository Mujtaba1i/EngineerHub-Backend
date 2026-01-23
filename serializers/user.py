from pydantic import BaseModel

class UserRegistrationSchema(BaseModel):
    username: str
    email: str
    password: str

class UserSchema(BaseModel):
    username: str
    email: str
    # password: str

    class Config:
        orm_mode = True


class UserTokenSchema(BaseModel):
    token: str
    
    class Config:
        orm_mode = True

class UserLoginSchema(BaseModel):
    username: str
    password: str
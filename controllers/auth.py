from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserModel
from serializers.user import UserSchema, UserRegistrationSchema, UserLoginSchema, UserTokenSchema
from database import get_db

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def create_user(user: UserRegistrationSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter( (UserModel.username == user.username) | (UserModel.email == user.email) ).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    new_user = UserModel(username=user.username, email=user.email)
    new_user.set_password(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post('/login', response_model=UserTokenSchema)
def login(user: UserLoginSchema, db: Session = Depends(get_db)):

    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    
    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = db_user.generate_token()
    return {"token": token, "message": "Login successful"}
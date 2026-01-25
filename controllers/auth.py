from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserModel, UserRole
from serializers.user import UserSchema, UserRegistrationSchema, UserLoginSchema, UserTokenSchema
from database import get_db

router = APIRouter()

ROLE_REQUIRED_FIELDS = {
    "doctor": ["department", "phone_num", "office_num"],
    "student": ["uni_id", "phone_num", "major"],
    "graduate": ["uni_id", "phone_num", "major"],
    "institution": ["phone_num", "license"],
}

def validate_user_by_role(role: str, user):
    required_fields = ROLE_REQUIRED_FIELDS.get(role, [])

    missing_fields = [ field for field in required_fields if getattr(user, field) is None]
    if missing_fields:
        raise HTTPException(status_code=400,detail=f"Missing required fields for role '{role}': {', '.join(missing_fields)}")


@router.post("/auth/register", response_model=UserTokenSchema)
def create_user(user: UserRegistrationSchema, db: Session = Depends(get_db)):
    print('test')
    existing_user = db.query(UserModel).filter( (UserModel.name == user.name) | (UserModel.email == user.email) ).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="name or email already exists")
    
    validate_user_by_role(user.role, user)

    new_user = UserModel(name=user.name, email=user.email, role=UserRole(user.role), major=user.major, uni_id=user.uni_id, department=user.department, phone_num=user.phone_num, office_num=user.office_num, license=user.license)
    new_user.set_password(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = new_user.generate_token()
    return {"token": token, "message": "Registration successful"}

@router.post('/auth/login', response_model=UserTokenSchema)
def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    if user.name:
        db_user = db.query(UserModel).filter(UserModel.name == user.name).first()
    

    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail=f"Invalid credintials")
    
    token = db_user.generate_token()
    return {"token": token, "message": "Login successful"}
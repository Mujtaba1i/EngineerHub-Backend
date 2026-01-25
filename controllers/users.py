from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserModel
from serializers.user import UserSchema
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()

# GET ALL ============================================================================
@router.get("/users", response_model=list[UserSchema])
def get_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

# GET ONE ===========================================================================
@router.get("/users/{user_id}", response_model=UserSchema)
def get_single_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# UPDATE =============================================================================
# @router.put("/users/{user_id}", response_model=UserSchema)
# def update_user(user_id: int, user: UpdateUserSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
#     db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if db_user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Operation forbidden")

#     user_data = user.dict(exclude_unset=True)
#     for key, value in user_data.items():
#         setattr(db_user, key, value)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# DELETE ===============================================================================
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Operation forbidden")

    db.delete(db_user)
    db.commit()
    return {"message": f"User with ID {user_id} has been deleted"}

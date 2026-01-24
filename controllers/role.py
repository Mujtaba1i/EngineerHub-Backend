from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.role import RoleModel
from serializers.role import RoleSchema, RoleCreateSchema
from database import get_db

router = APIRouter()

@router.post("/roles", response_model=RoleSchema)
def create_role(role: RoleCreateSchema, db: Session = Depends(get_db)):
    new_role = RoleModel(
        user_id=role.user_id,
        major=role.major,
        department=role.department,
        approval=role.approval
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.get("/roles", response_model=list[RoleSchema])
def get_roles(db: Session = Depends(get_db)):
    return db.query(RoleModel).all()

@router.put("/roles/{role_id}/approve")
def approve_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.approval = True
    db.commit()
    return {"message": "Role approved"}

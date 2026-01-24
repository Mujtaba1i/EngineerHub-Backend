from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.role import RoleModel
from serializers.role import RoleSchema, CreateRoleSchema,UpdateRoleSchema
from database import get_db

router = APIRouter()

# GET ALL ============================================================================
@router.get("/roles", response_model=list[RoleSchema])
def get_roles(db: Session = Depends(get_db)):
    return db.query(RoleModel).all()

# GET ONE ===========================================================================
@router.get("/roles/{role_id}", response_model=RoleSchema)
def get_single_user(role_id: int, db: Session = Depends(get_db)):
    user = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# CREATE ============================================================================
@router.post("/roles", response_model=RoleSchema)
def create_role(role: CreateRoleSchema, db: Session = Depends(get_db)):
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

# UPDATE =============================================================================
@router.put("/roles/{role_id}/approve")
def approve_role(role_id: int,role:UpdateRoleSchema, db: Session = Depends(get_db)):
    role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.approval = True
    db.commit()
    return {"message": "Role approved"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.classes import ClassModel
from models.user import UserModel , UserRole
from serializers.class_serializer import ClassSchema,CreateClassSchema,UpdateClassSchema
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter() 

# GET ALL ===================================================================================
@router.get("/classes", response_model=list[ClassSchema])
def get_classes(db: Session = Depends(get_db)):
    return db.query(ClassModel).all()

# GET ONE ===================================================================================
@router.get("/classes/{class_id}", response_model=ClassSchema)
def get_single_class(class_id: int, db: Session = Depends(get_db)):
    cls = db.query(ClassModel).filter(ClassModel.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls

# CREATE ===================================================================================
@router.post("/classes", response_model=ClassSchema) 
def create_class(
    data: CreateClassSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(403, "Only doctors can create classes")

    new_class = ClassModel(
        name=data.name,
        doctor_id=current_user.user_roles[0].id
    )

    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

# ONLY DR CAN CREATE CLASSES

# UPDATE ================================================================
@router.put("/classes/{class_id}", response_model=ClassSchema)
def update_class(
    class_id: int,
    data: UpdateClassSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    cls = db.query(ClassModel).filter(ClassModel.id == class_id).first()

    if not cls:
        raise HTTPException(404, "Class not found")

    if cls.doctor_id != current_user.user_roles[0].id:
        raise HTTPException(403, "Not allowed")

    cls.name = data.name
    db.commit()
    db.refresh(cls)
    return cls

# DELETE =================================================================
@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    cls = db.query(ClassModel).filter(ClassModel.id == class_id).first()

    if not cls:
        raise HTTPException(404, "Class not found")

    if cls.doctor_id != current_user.user_roles[0].id:
        raise HTTPException(403, "Not allowed")

    db.delete(cls)
    db.commit()
    return {"message": "Class deleted"}





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.classes import ClassModel
from serializers.class_ import ClassSchema
from database import get_db

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
def create_class(class_data: ClassSchema, db: Session = Depends(get_db)):
    new_class = ClassModel(name=class_data.name, doctor_id=class_data.doctor_id)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class
# ONLY DR CAN CREATE CLASSES


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.student_class import StudentClassModel
from models.user import UserModel
from serializers.student_class import (StudentClassSchema, CreateStudentClassSchema )
from database import get_db

router = APIRouter()


# ADD STUDENTS IN THE CLASSES ===========================================================
@router.post("/students-classes")
def add_student(data: CreateStudentClassSchema, db: Session = Depends(get_db)):
    student = db.query(UserModel).filter( UserModel.uni_id == data.uni_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    exists = db.query(StudentClassModel).filter(
        StudentClassModel.student_id == student.id,
        StudentClassModel.class_id == data.class_id
    ).first()

    if exists:
        raise HTTPException(status_code=409, detail="Already enrolled")

    enrollment = StudentClassModel(
        student_id=student.id,
        class_id=data.class_id
    )

    db.add(enrollment)
    db.commit()
    return {"message": "Student added to class"}

# LEAVE STUDENTS =========================================================================================
@router.delete("/students-classes/{class_id}/{student_id}")
def remove_student(class_id: int, student_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(StudentClassModel).filter(
        StudentClassModel.student_id == student_id,
        StudentClassModel.class_id == class_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()
    return {"message": "Student removed from class"}

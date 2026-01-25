from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.student_class import StudentClassModel
from models.user import UserModel, UserRole
from models.classes import ClassModel
from serializers.student_class import (StudentClassSchema, CreateStudentClassSchema )
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()


# ADD STUDENTS IN THE CLASSES ===========================================================
@router.post("/students-classes")
def add_student(
    data: CreateStudentClassSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can add students")


    cls = db.query(ClassModel).filter(ClassModel.id == data.class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    if cls.doctor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this class"
        )

    student = db.query(UserModel).filter(
        UserModel.id == data.student_id
    ).first()

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
def remove_student(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # 1️⃣ نتأكد إن الكلاس موجود
    cls = db.query(ClassModel).filter(ClassModel.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # 2️⃣ نتحقق من الصلاحيات
    is_owner_doctor = (
        current_user.role == UserRole.DOCTOR
        and cls.doctor_id == current_user.id
    )

    is_self_student = (
        current_user.role == UserRole.STUDENT
        and current_user.id == student_id
    )

    if not (is_owner_doctor or is_self_student):
        raise HTTPException(
            status_code=403,
            detail="Not allowed to remove this student"
        )

    # 3️⃣ نتأكد إن التسجيل موجود
    enrollment = db.query(StudentClassModel).filter(
        StudentClassModel.student_id == student_id,
        StudentClassModel.class_id == class_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Student not enrolled in this class"
        )

    db.delete(enrollment)
    db.commit()

    return {"message": "Student removed from class"}

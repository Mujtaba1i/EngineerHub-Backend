from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.announcement import AnnouncementModel
from models.classes import ClassModel
from models.user import UserModel, UserRole
from serializers.announcement_serializer import (AnnouncementSchema, CreateAnnouncementSchema, UpdateAnnouncementSchema)
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()

# GET ALL ANNOUNCEMENTS FOR A CLASS ================================================
@router.get("/classes/{class_id}/announcements", response_model=list[AnnouncementSchema])
def get_class_announcements(
    class_id: int,
    db: Session = Depends(get_db)
):
    cls = db.query(ClassModel).filter(ClassModel.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    announcements = db.query(AnnouncementModel).filter(
        AnnouncementModel.class_id == class_id
    ).order_by(AnnouncementModel.event_date.desc()).all()
    
    return announcements

# GET ANNOUNCEMENTS FOR ALL STUDENT'S CLASSES ========================================
@router.get("/my-announcements", response_model=list[AnnouncementSchema])
def get_my_announcements(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    # Get all class IDs the student is enrolled in
    class_ids = [enrollment.class_id for enrollment in current_user.enrollments]
    
    # Get all announcements for those classes
    announcements = db.query(AnnouncementModel).filter(
        AnnouncementModel.class_id.in_(class_ids)
    ).order_by(AnnouncementModel.event_date.desc()).all()
    
    return announcements

# CREATE ANNOUNCEMENT (DOCTOR ONLY) ================================================
@router.post("/announcements", response_model=AnnouncementSchema)
def create_announcement(
    data: CreateAnnouncementSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can create announcements")
    
    # Verify the class exists and belongs to the doctor
    cls = db.query(ClassModel).filter(ClassModel.id == data.class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if cls.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only create announcements for your own classes")
    
    new_announcement = AnnouncementModel(
        title=data.title,
        content=data.content,
        event_date=data.event_date,
        class_id=data.class_id
    )
    
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    
    return new_announcement

# UPDATE ANNOUNCEMENT (DOCTOR ONLY) ================================================
@router.put("/announcements/{announcement_id}", response_model=AnnouncementSchema)
def update_announcement(
    announcement_id: int,
    data: UpdateAnnouncementSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can update announcements")
    
    announcement = db.query(AnnouncementModel).filter(
        AnnouncementModel.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Verify the doctor owns the class
    cls = db.query(ClassModel).filter(ClassModel.id == announcement.class_id).first()
    if cls.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Update fields
    if data.title is not None:
        announcement.title = data.title
    if data.content is not None:
        announcement.content = data.content
    if data.event_date is not None:
        announcement.event_date = data.event_date
    
    db.commit()
    db.refresh(announcement)
    
    return announcement

# DELETE ANNOUNCEMENT (DOCTOR ONLY) ================================================
@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can delete announcements")
    
    announcement = db.query(AnnouncementModel).filter(
        AnnouncementModel.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Verify the doctor owns the class
    cls = db.query(ClassModel).filter(ClassModel.id == announcement.class_id).first()
    if cls.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    db.delete(announcement)
    db.commit()
    
    return {"message": "Announcement deleted"}
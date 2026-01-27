from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from models.note import NoteModel, NoteLikeModel
from models.user import UserModel, UserRole
from serializers.note_serializer import (
    NoteSchema,
    CreateNoteSchema,
    UpdateNoteSchema,
    NoteLikeSchema
)
from database import get_db
from dependencies.get_current_user import get_current_user
from services.s3_service import s3_service

router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def get_file_type(filename: str) -> str:
    """Get file type from filename"""
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return 'pdf'
    elif ext in ['doc', 'docx']:
        return 'document'
    elif ext in ['png', 'jpg', 'jpeg', 'gif']:
        return 'image'
    return 'other'


# GET ALL NOTES ================================================================
@router.get("/notes", response_model=List[NoteSchema])
def get_all_notes(
    course_code: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all notes with optional filters"""
    query = db.query(NoteModel)
    
    # Apply filters
    if course_code:
        query = query.filter(NoteModel.course_code.ilike(f"%{course_code}%"))
    if year:
        query = query.filter(NoteModel.year == year)
    if search:
        query = query.filter(
            (NoteModel.title.ilike(f"%{search}%")) |
            (NoteModel.description.ilike(f"%{search}%")) |
            (NoteModel.doctor_name.ilike(f"%{search}%"))
        )
    
    notes = query.order_by(NoteModel.created_at.desc()).all()
    
    # Add download URLs and user like status
    result = []
    for note in notes:
        note_dict = NoteSchema.from_orm(note).dict()
        
        # Generate download URL
        try:
            note_dict['download_url'] = s3_service.generate_presigned_url(note.file_key)
        except Exception as e:
            print(f"Error generating URL for {note.file_key}: {e}")
            note_dict['download_url'] = None
        
        # Get user's like status
        user_like = db.query(NoteLikeModel).filter(
            NoteLikeModel.note_id == note.id,
            NoteLikeModel.user_id == current_user.id
        ).first()
        note_dict['user_like_status'] = user_like.is_like if user_like else None
        
        result.append(note_dict)
    
    return result


# GET SINGLE NOTE ==============================================================
@router.get("/notes/{note_id}", response_model=NoteSchema)
def get_single_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get a single note by ID"""
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_dict = NoteSchema.from_orm(note).dict()
    
    # Generate download URL
    try:
        note_dict['download_url'] = s3_service.generate_presigned_url(note.file_key)
    except Exception as e:
        note_dict['download_url'] = None
    
    # Get user's like status
    user_like = db.query(NoteLikeModel).filter(
        NoteLikeModel.note_id == note.id,
        NoteLikeModel.user_id == current_user.id
    ).first()
    note_dict['user_like_status'] = user_like.is_like if user_like else None
    
    return note_dict


# UPLOAD NOTE ==================================================================
@router.post("/notes", response_model=NoteSchema)
async def upload_note(
    file: UploadFile = File(...),
    title: str = Form(...),
    course_code: str = Form(...),
    year: int = Form(...),
    doctor_name: str = Form(...),
    course_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Upload a new note (students and graduates only)"""
    
    # Check user role
    if current_user.role not in [UserRole.STUDENT, UserRole.GRADUATE]:
        raise HTTPException(
            status_code=403,
            detail="Only students and graduates can upload notes"
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Upload to S3
    try:
        file_key = s3_service.upload_file(
            file_content,
            file.filename,
            file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    # Create note record in database
    new_note = NoteModel(
        title=title,
        file_name=file.filename,
        file_key=file_key,
        file_type=get_file_type(file.filename),
        file_size=file_size,
        course_code=course_code,
        course_name=course_name,
        year=year,
        doctor_name=doctor_name,
        description=description,
        uploader_id=current_user.id,
        likes_count=0,
        dislikes_count=0
    )
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    # Return with download URL
    note_dict = NoteSchema.from_orm(new_note).dict()
    try:
        note_dict['download_url'] = s3_service.generate_presigned_url(new_note.file_key)
    except:
        note_dict['download_url'] = None
    note_dict['user_like_status'] = None
    
    return note_dict


# UPDATE NOTE METADATA =========================================================
@router.put("/notes/{note_id}", response_model=NoteSchema)
def update_note(
    note_id: int,
    data: UpdateNoteSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update note metadata (only by uploader)"""
    
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Only uploader can edit
    if note.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own notes")
    
    # Update fields
    if data.title is not None:
        note.title = data.title
    if data.course_code is not None:
        note.course_code = data.course_code
    if data.course_name is not None:
        note.course_name = data.course_name
    if data.year is not None:
        note.year = data.year
    if data.doctor_name is not None:
        note.doctor_name = data.doctor_name
    if data.description is not None:
        note.description = data.description
    
    db.commit()
    db.refresh(note)
    
    # Return with download URL
    note_dict = NoteSchema.from_orm(note).dict()
    try:
        note_dict['download_url'] = s3_service.generate_presigned_url(note.file_key)
    except:
        note_dict['download_url'] = None
    
    # Get user's like status
    user_like = db.query(NoteLikeModel).filter(
        NoteLikeModel.note_id == note.id,
        NoteLikeModel.user_id == current_user.id
    ).first()
    note_dict['user_like_status'] = user_like.is_like if user_like else None
    
    return note_dict


# DELETE NOTE ==================================================================
@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a note (only by uploader)"""
    
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Only uploader can delete
    if note.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own notes")
    
    # Delete from S3
    try:
        s3_service.delete_file(note.file_key)
    except Exception as e:
        print(f"Error deleting from S3: {e}")
        # Continue with database deletion even if S3 deletion fails
    
    # Delete from database
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}


# LIKE/DISLIKE NOTE ============================================================
@router.post("/notes/{note_id}/like")
def like_note(
    note_id: int,
    is_like: int = Form(...),  # 1 for like, -1 for dislike
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Like or dislike a note"""
    
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Validate is_like value
    if is_like not in [1, -1]:
        raise HTTPException(status_code=400, detail="is_like must be 1 or -1")
    
    # Check if user already liked/disliked
    existing_like = db.query(NoteLikeModel).filter(
        NoteLikeModel.note_id == note_id,
        NoteLikeModel.user_id == current_user.id
    ).first()
    
    if existing_like:
        # If same action, remove it (toggle off)
        if existing_like.is_like == is_like:
            # Update counts
            if is_like == 1:
                note.likes_count = max(0, note.likes_count - 1)
            else:
                note.dislikes_count = max(0, note.dislikes_count - 1)
            
            db.delete(existing_like)
            db.commit()
            return {"message": "Reaction removed", "likes": note.likes_count, "dislikes": note.dislikes_count}
        else:
            # Change from like to dislike or vice versa
            if existing_like.is_like == 1:
                note.likes_count = max(0, note.likes_count - 1)
                note.dislikes_count += 1
            else:
                note.dislikes_count = max(0, note.dislikes_count - 1)
                note.likes_count += 1
            
            existing_like.is_like = is_like
            db.commit()
            return {"message": "Reaction updated", "likes": note.likes_count, "dislikes": note.dislikes_count}
    else:
        # Create new like/dislike
        new_like = NoteLikeModel(
            note_id=note_id,
            user_id=current_user.id,
            is_like=is_like
        )
        
        # Update counts
        if is_like == 1:
            note.likes_count += 1
        else:
            note.dislikes_count += 1
        
        db.add(new_like)
        db.commit()
        
        return {"message": "Reaction added", "likes": note.likes_count, "dislikes": note.dislikes_count}
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
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
from config.environment import get_settings
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta

router = APIRouter()

settings = get_settings()
AZURE_STORAGE_ACCOUNT = settings.AZURE_STORAGE_ACCOUNT_NAME
AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_ACCOUNT_KEY
AZURE_CONTAINER_NAME = settings.AZURE_STORAGE_CONTAINER_NAME

try:
    azure_blob_client = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
        account_name=AZURE_STORAGE_ACCOUNT,
        account_key=AZURE_STORAGE_ACCOUNT_KEY
    )
    container_client = azure_blob_client.get_container_client(AZURE_CONTAINER_NAME)
except Exception as e:
    print(f"Warning: Could not initialize Azure client: {e}")
    container_client = None

def blob_exists_in_azure(file_key: str) -> bool:
    try:
        if not container_client:
            return True
        
        blob_client = container_client.get_blob_client(file_key)
        blob_client.get_blob_properties()
        return True
    except Exception as e:
        return False

class CreateNoteFromAzureRequest(BaseModel):
    title: str
    file_name: str
    file_key: str
    file_type: str
    file_size: int
    course_code: str
    course_name: Optional[str] = None
    year: int
    doctor_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024

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
        
        # Set download URL (Azure blob key)
        note_dict['download_url'] = note.file_key
        
        # Get user's like status
        user_like = db.query(NoteLikeModel).filter(
            NoteLikeModel.note_id == note.id,
            NoteLikeModel.user_id == current_user.id
        ).first()
        note_dict['user_like_status'] = user_like.is_like if user_like else None
        
        result.append(note_dict)
    
    return result


# LIST AZURE FILES FOR USER ====================================================
class OrphanedFileResponse(BaseModel):
    file_key: str
    file_name: str
    created_at: Optional[str] = None
    size: Optional[int] = None

class ListOrphanedFilesResponse(BaseModel):
    files: List[OrphanedFileResponse]
    count: int
    message: str
    error: Optional[str] = None

    class Config:
        from_attributes = True

# GET EXISTING FILE KEYS FOR DATABASE ============================================
@router.get("/notes/existing-file-keys")
def get_existing_file_keys(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    try:
        # Get all file_keys for current user
        existing_keys = db.query(NoteModel.file_key).filter(
            NoteModel.uploader_id == current_user.id
        ).all()
        
        file_keys_list = [row[0] for row in existing_keys]
        
        return {
            "file_keys": file_keys_list,
            "count": len(file_keys_list),
            "message": f"Found {len(file_keys_list)} notes uploaded by you"
        }
    except Exception as e:
        return {
            "file_keys": [],
            "error": str(e),
            "message": "Could not retrieve file keys"
        }

@router.get("/notes/my-azure-files", response_model=ListOrphanedFilesResponse)
def list_user_azure_files(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    try:
        if not container_client:
            return ListOrphanedFilesResponse(files=[], count=0, message="Cannot access Azure storage")
        
        # List all blobs in the container
        blobs = container_client.list_blobs()
        
        # Filter blobs that are in user's directory (notes/{user_id}/)
        # For now, just get files created by the current user
        all_blobs = list(blobs)
        print(f"DEBUG: Found {len(all_blobs)} total blobs in Azure container")
        for blob in all_blobs:
            print(f"DEBUG: Blob - {blob.name} (size: {blob.size})")
        
        # Get all existing file_keys in the database
        existing_file_keys = db.query(NoteModel.file_key).all()
        existing_keys_set = {row[0] for row in existing_file_keys}
        print(f"DEBUG: Found {len(existing_keys_set)} notes in database")
        for key in existing_keys_set:
            print(f"DEBUG: DB key - {key}")
        
        # Find files that exist in Azure but not in database
        orphaned_files = []
        for blob in all_blobs:
            if blob.name not in existing_keys_set:
                orphaned_files.append(OrphanedFileResponse(
                    file_key=blob.name,
                    file_name=blob.name.split('/')[-1],
                    created_at=blob.creation_time.isoformat() if blob.creation_time else None,
                    size=blob.size
                ))
        
        return ListOrphanedFilesResponse(
            files=orphaned_files,
            count=len(orphaned_files),
            message=f"Found {len(orphaned_files)} files in Azure without database records"
        )
    except Exception as e:
        return ListOrphanedFilesResponse(
            files=[],
            count=0,
            message="Could not list Azure files",
            error=str(e)
        )


# GET SINGLE NOTE ==============================================================
@router.get("/notes/{note_id}", response_model=NoteSchema)
def get_single_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_dict = NoteSchema.from_orm(note).dict()
    
    # Set download URL (Azure blob key)
    note_dict['download_url'] = note.file_key
    
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
    note_data: CreateNoteFromAzureRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    
    # Check user role
    if current_user.role not in [UserRole.STUDENT, UserRole.GRADUATE]:
        raise HTTPException(
            status_code=403,
            detail="Only students and graduates can upload notes"
        )
    
    # Validate file size
    if note_data.file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate file type
    file_extension = '.' + note_data.file_name.split('.')[-1].lower() if '.' in note_data.file_name else ''
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create note record in database
    new_note = NoteModel(
        title=note_data.title,
        file_name=note_data.file_name,
        file_key=note_data.file_key,
        file_type=note_data.file_type,
        file_size=note_data.file_size,
        course_code=note_data.course_code,
        course_name=note_data.course_name,
        year=note_data.year,
        doctor_name=note_data.doctor_name,
        description=note_data.description,
        uploader_id=current_user.id,
        likes_count=0,
        dislikes_count=0
    )
    
    print(f"DEBUG: Creating note - file_key: {note_data.file_key}, uploader_id: {current_user.id}")
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    print(f"DEBUG: Note created with ID: {new_note.id}")
    
    # Return response
    note_dict = NoteSchema.from_orm(new_note).dict()
    note_dict['download_url'] = note_data.file_key  # URL is the Azure blob key
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
    note_dict['download_url'] = note.file_key
    
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
    
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Only uploader can delete
    if note.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own notes")
    
    # Return file_key so frontend can delete from Azure
    file_key = note.file_key
    
    # Delete from database
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully", "file_key": file_key}


# LIKE/DISLIKE NOTE ============================================================
@router.post("/notes/{note_id}/like")
def like_note(
    note_id: int,
    is_like: int = Form(...),  # 1 for like, -1 for dislike
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    
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


# RECOVER ORPHANED AZURE FILE =================================================
class RecoverFileResponse(BaseModel):
    message: str
    note: NoteSchema

    class Config:
        from_attributes = True

@router.post("/notes/recover-file", response_model=RecoverFileResponse)
def recover_azure_file(
    file_key: str = Query(...),
    title: str = Query(...),
    course_code: str = Query(...),
    year: int = Query(...),
    doctor_name: str = Query(...),
    course_name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    
    # Check user role
    if current_user.role not in [UserRole.STUDENT, UserRole.GRADUATE]:
        raise HTTPException(
            status_code=403,
            detail="Only students and graduates can upload notes"
        )
    
    # Check if file already has a record
    existing_note = db.query(NoteModel).filter(NoteModel.file_key == file_key).first()
    if existing_note:
        raise HTTPException(
            status_code=400,
            detail="This file already has a note record in the database"
        )
    
    # Check if file exists in Azure
    try:
        blob_client = container_client.get_blob_client(file_key)
        blob_properties = blob_client.get_blob_properties()
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"File not found in Azure storage: {str(e)}"
        )
    
    # Extract filename and type from file_key
    file_name = file_key.split('/')[-1]
    file_type = get_file_type(file_name)
    file_size = blob_properties.size
    
    # Validate file type
    file_extension = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create note record in database
    new_note = NoteModel(
        title=title,
        file_name=file_name,
        file_key=file_key,
        file_type=file_type,
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
    
    # Return response
    note_dict = NoteSchema.from_orm(new_note).dict()
    note_dict['download_url'] = new_note.file_key
    note_dict['user_like_status'] = None
    
    return RecoverFileResponse(
        message="File recovered and note record created",
        note=note_dict
    )
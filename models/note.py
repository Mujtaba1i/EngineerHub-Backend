from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class NoteModel(BaseModel):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    title = Column(String, nullable=False)
    file_name = Column(String, nullable=False)  # Original filename
    file_key = Column(String, nullable=False, unique=True)  # S3 key/path
    file_type = Column(String, nullable=False)  # pdf, docx, image, etc.
    file_size = Column(Integer, nullable=True)  # in bytes
    
    # Course information
    course_code = Column(String, nullable=False)
    course_name = Column(String, nullable=True)
    year = Column(Integer, nullable=False)  # Year the course was taught
    doctor_name = Column(String, nullable=False)
    
    # Additional info
    description = Column(Text, nullable=True)
    
    # Uploader information
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Likes/Dislikes count
    likes_count = Column(Integer, default=0)
    dislikes_count = Column(Integer, default=0)
    
    # Relationships
    uploader = relationship("UserModel", back_populates="notes", passive_deletes=True)
    likes = relationship("NoteLikeModel", back_populates="note", cascade="all, delete-orphan", passive_deletes=True)


class NoteLikeModel(BaseModel):
    __tablename__ = "note_likes"

    id = Column(Integer, primary_key=True, index=True)
    
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # True for like, False for dislike
    is_like = Column(Integer, nullable=False)  # 1 for like, -1 for dislike
    
    # Relationships
    note = relationship("NoteModel", back_populates="likes", passive_deletes=True)
    user = relationship("UserModel", back_populates="note_likes", passive_deletes=True)
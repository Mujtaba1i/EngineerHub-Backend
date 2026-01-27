from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class AnnouncementModel(BaseModel):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    event_date = Column(DateTime, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)

    # Relationship
    class_ = relationship("ClassModel", back_populates="announcements", passive_deletes=True)
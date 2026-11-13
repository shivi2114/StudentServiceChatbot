from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import Announcement, User
from backend.app.schemas.all_schemas import AnnouncementResponse, AnnouncementCreate
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("", response_model=List[AnnouncementResponse])
def get_announcements(db: Session = Depends(get_db)):
    """Retrieve all campus announcements, latest first."""
    return db.query(Announcement).order_by(Announcement.id.desc()).all()


@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(
    payload: AnnouncementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to publish a new announcement."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    announcement = Announcement(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        published_date=payload.published_date,
        is_urgent=payload.is_urgent,
        target_branch=payload.target_branch
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

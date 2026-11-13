from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import (
    User, StudentProfile, AcademicRecord, FeeRecord,
    Complaint, Announcement, Notification
)
from backend.app.schemas.all_schemas import (
    StudentProfileResponse, AcademicRecordResponse, FeeRecordResponse,
    ComplaintResponse, AnnouncementResponse, NotificationResponse,
    StudentFullDashboardResponse
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/students", tags=["Students"])


def _get_student_for_user(user: User, db: Session) -> StudentProfile:
    student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )
    return student


@router.get("/me", response_model=StudentProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve logged-in student profile."""
    student = _get_student_for_user(current_user, db)
    return StudentProfileResponse(
        id=student.id,
        user_id=student.user_id,
        roll_number=student.roll_number,
        branch=student.branch,
        semester=student.semester,
        section=student.section,
        cgpa=student.cgpa,
        phone=student.phone,
        hostel_resident=student.hostel_resident,
        room_number=student.room_number,
        full_name=current_user.full_name,
        email=current_user.email
    )


@router.get("/dashboard", response_model=StudentFullDashboardResponse)
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve aggregated data for student dashboard."""
    student = _get_student_for_user(current_user, db)

    # Academics
    academics = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).all()
    overall_attendance = 0.0
    if academics:
        overall_attendance = round(sum(a.attendance_percentage for a in academics) / len(academics), 1)

    # Fees
    fees = db.query(FeeRecord).filter(FeeRecord.student_id == student.id).all()
    total_due = sum(f.due_amount for f in fees)

    # Recent Complaints
    complaints = db.query(Complaint).filter(Complaint.student_id == student.id).order_by(Complaint.created_at.desc()).limit(5).all()

    # Announcements
    announcements = db.query(Announcement).order_by(Announcement.id.desc()).limit(5).all()

    # Notifications
    notifications = db.query(Notification).filter(
        Notification.student_id == student.id,
        Notification.is_active == True
    ).order_by(Notification.created_at.desc()).limit(5).all()

    profile_resp = StudentProfileResponse(
        id=student.id,
        user_id=student.user_id,
        roll_number=student.roll_number,
        branch=student.branch,
        semester=student.semester,
        section=student.section,
        cgpa=student.cgpa,
        phone=student.phone,
        hostel_resident=student.hostel_resident,
        room_number=student.room_number,
        full_name=current_user.full_name,
        email=current_user.email
    )

    return StudentFullDashboardResponse(
        profile=profile_resp,
        academics=academics,
        overall_attendance=overall_attendance,
        fees=fees,
        total_due=total_due,
        recent_complaints=complaints,
        announcements=announcements,
        notifications=notifications
    )


@router.get("/academics", response_model=List[AcademicRecordResponse])
def get_academic_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = _get_student_for_user(current_user, db)
    return db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).all()


@router.get("/fees", response_model=List[FeeRecordResponse])
def get_fee_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = _get_student_for_user(current_user, db)
    return db.query(FeeRecord).filter(FeeRecord.student_id == student.id).all()


@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    student = _get_student_for_user(current_user, db)
    return db.query(Notification).filter(Notification.student_id == student.id).order_by(Notification.created_at.desc()).all()

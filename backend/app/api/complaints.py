import random
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import User, StudentProfile, Complaint
from backend.app.schemas.all_schemas import (
    ComplaintCreate, ComplaintResponse, ComplaintUpdate, ComplaintEscalate
)
from backend.app.services.auth_service import get_current_user

router = APIRouter(prefix="/complaints", tags=["Complaints"])


def _generate_ticket_id(db: Session) -> str:
    """Generate unique ticket ID format: CMP-2026-XXXX."""
    while True:
        num = random.randint(1000, 9999)
        ticket = f"CMP-2026-{num}"
        exists = db.query(Complaint).filter(Complaint.ticket_id == ticket).first()
        if not exists:
            return ticket


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def file_complaint(
    payload: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """File a new student complaint ticket."""
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only registered students can file complaints."
        )

    ticket_id = _generate_ticket_id(db)
    complaint = Complaint(
        ticket_id=ticket_id,
        student_id=student.id,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        priority=payload.priority.upper(),
        status="PENDING"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=List[ComplaintResponse])
def list_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List complaints for the current student or all complaints if admin."""
    if current_user.role == "admin":
        return db.query(Complaint).order_by(Complaint.created_at.desc()).all()

    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        return []
    return db.query(Complaint).filter(Complaint.student_id == student.id).order_by(Complaint.created_at.desc()).all()


@router.get("/{ticket_id}", response_model=ComplaintResponse)
def get_complaint(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve details and status for a specific complaint ticket."""
    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id.strip()).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ticket ID '{ticket_id}' not found."
        )

    # If student, ensure ticket belongs to them
    if current_user.role != "admin":
        student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not student or complaint.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this ticket."
            )

    return complaint


@router.post("/{ticket_id}/escalate", response_model=ComplaintResponse)
def escalate_complaint(
    ticket_id: str,
    payload: ComplaintEscalate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Escalate a pending or in-review complaint to the Proctorial / Dean Board."""
    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id.strip()).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found."
        )

    if current_user.role != "admin":
        student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not student or complaint.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied."
            )

    complaint.status = "ESCALATED"
    complaint.priority = "CRITICAL"
    reason_note = f"[Escalated by {current_user.full_name}]: {payload.reason}"
    if complaint.escalation_reason:
        complaint.escalation_reason += f"\n{reason_note}"
    else:
        complaint.escalation_reason = reason_note

    db.commit()
    db.refresh(complaint)
    return complaint


@router.patch("/{ticket_id}", response_model=ComplaintResponse)
def update_complaint_status(
    ticket_id: str,
    payload: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to update complaint status and resolution notes."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required to update tickets."
        )

    complaint = db.query(Complaint).filter(Complaint.ticket_id == ticket_id.strip()).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

    if payload.status:
        complaint.status = payload.status.upper()
    if payload.priority:
        complaint.priority = payload.priority.upper()
    if payload.escalation_reason:
        complaint.escalation_reason = payload.escalation_reason

    db.commit()
    db.refresh(complaint)
    return complaint

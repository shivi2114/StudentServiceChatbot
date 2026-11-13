import random
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.entities import (
    AcademicRecord, FeeRecord, Complaint, Notification, StudentProfile
)

# Reusing the 48 campus offices directory from the original chatbot for verified office routing
CAMPUS_SERVICE_DIRECTORY = {
    "admission": {"name": "Admission", "office": "Admission Cell", "contact": "Admission Portal & Campus Desk"},
    "eligibility": {"name": "Eligibility", "office": "Admission Cell", "contact": "Official Regulations Guide"},
    "documents": {"name": "Required Documents", "office": "Admission Cell", "contact": "Document Verification Counter"},
    "fees": {"name": "Fees Payment", "office": "Accounts Office", "contact": "ERP Portal / Accounts Counter (Windows 1-4)"},
    "fee_refund": {"name": "Fee Refund", "office": "Accounts Office", "contact": "Accounts Office Counter"},
    "hostel": {"name": "Hostel Allotment", "office": "Hostel Office", "contact": "Hostel Warden Office"},
    "hostel_fee": {"name": "Hostel Fee", "office": "Hostel Office", "contact": "Hostel Administration Counter"},
    "mess": {"name": "Hostel Mess", "office": "Hostel Office", "contact": "Hostel Notice Board & Dining Hall Desk"},
    "library": {"name": "Central Library", "office": "Central Library", "contact": "Circulation Counter (9:00 AM - 8:00 PM)"},
    "exam_schedule": {"name": "Examination Schedule", "office": "Examination Cell", "contact": "University Portal / Exam Notice Board Counter 3"},
    "result": {"name": "Semester Results", "office": "Examination Cell", "contact": "University Portal & Exam Cell"},
    "revaluation": {"name": "Result Revaluation", "office": "Examination Cell", "contact": "Examination Cell Counter 3"},
    "back_paper": {"name": "Back Paper Registration", "office": "Examination Cell", "contact": "ERP Portal / Examination Cell Desk"},
    "attendance": {"name": "Attendance Requirement", "office": "Academic Department", "contact": "Class Mentor / HOD Office"},
    "scholarship": {"name": "Scholarships", "office": "Scholarship Cell", "contact": "Student Welfare Section Counter 4"},
    "placement": {"name": "Campus Placements", "office": "Training & Placement Cell", "contact": "Placement Complex, Block C"},
    "internship": {"name": "Internships", "office": "Training & Placement Cell", "contact": "T&P Desk & HOD Office"},
    "wifi": {"name": "Campus Wi-Fi", "office": "IT Support Desk", "contact": "Computer Center Ground Floor"},
    "erp": {"name": "Student ERP Portal", "office": "IT Support / ERP Cell", "contact": "ERP Portal Desk"},
    "medical": {"name": "Medical Assistance", "office": "Campus Health Center", "contact": "Residential Block A Ground Floor (24x7)"},
    "anti_ragging": {"name": "Anti-Ragging Helpline", "office": "Anti-Ragging Committee", "contact": "Toll-Free 1800-180-5522 / Proctor Office"},
    "complaint": {"name": "Student Grievance", "office": "Grievance Redressal Cell", "contact": "Dean Student Welfare Office"}
}


def lookup_campus_office(query: str) -> Optional[Dict[str, str]]:
    """Match query against verified campus service directory."""
    q = query.lower()
    for key, val in CAMPUS_SERVICE_DIRECTORY.items():
        if key in q:
            return {"office": val["office"], "contact": val["contact"], "service": val["name"]}
    return None


def get_student_academic_summary(student_id: int, db: Session) -> Dict[str, Any]:
    """Retrieve verified attendance and marks records for a student."""
    records = db.query(AcademicRecord).filter(AcademicRecord.student_id == student_id).all()
    if not records:
        return {"found": False, "message": "No academic records found."}

    results = []
    low_attendance_warnings = []
    total_att = 0.0

    for r in records:
        results.append({
            "subject_code": r.subject_code,
            "subject_name": r.subject_name,
            "attendance": r.attendance_percentage,
            "total_classes": r.total_classes,
            "attended": r.attended_classes,
            "internal_marks": r.internal_marks
        })
        total_att += r.attendance_percentage
        if r.attendance_percentage < 75.0:
            low_attendance_warnings.append({
                "subject": f"{r.subject_code} ({r.subject_name})",
                "attendance": r.attendance_percentage,
                "deficit": round(75.0 - r.attendance_percentage, 1)
            })

    avg_attendance = round(total_att / len(records), 1)

    return {
        "found": True,
        "courses": results,
        "average_attendance": avg_attendance,
        "is_overall_eligible": avg_attendance >= 75.0,
        "low_attendance_warnings": low_attendance_warnings
    }


def get_student_fee_summary(student_id: int, db: Session) -> Dict[str, Any]:
    """Retrieve verified fee records and pending dues."""
    records = db.query(FeeRecord).filter(FeeRecord.student_id == student_id).all()
    if not records:
        return {"found": False, "message": "No fee ledger records found."}

    results = []
    total_due = 0.0
    for f in records:
        results.append({
            "semester": f.semester,
            "total_amount": f.total_amount,
            "paid_amount": f.paid_amount,
            "due_amount": f.due_amount,
            "due_date": f.due_date,
            "status": f.status,
            "payment_ref": f.payment_ref
        })
        total_due += f.due_amount

    return {
        "found": True,
        "records": results,
        "total_due_amount": total_due,
        "has_pending_dues": total_due > 0.0
    }


def get_complaint_status_by_ticket(ticket_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Retrieve details for a specific complaint ticket."""
    c = db.query(Complaint).filter(Complaint.ticket_id == ticket_id.strip()).first()
    if not c:
        return None
    return {
        "ticket_id": c.ticket_id,
        "category": c.category,
        "title": c.title,
        "description": c.description,
        "priority": c.priority,
        "status": c.status,
        "escalation_reason": c.escalation_reason,
        "created_at": c.created_at.strftime("%Y-%m-%d %H:%M")
    }


def create_complaint_ticket_in_db(
    student_id: int,
    category: str,
    title: str,
    description: str,
    priority: str,
    db: Session
) -> Dict[str, Any]:
    """Create a new complaint ticket in the database with a unique ID."""
    while True:
        num = random.randint(1000, 9999)
        ticket = f"CMP-2026-{num}"
        if not db.query(Complaint).filter(Complaint.ticket_id == ticket).first():
            break

    complaint = Complaint(
        ticket_id=ticket,
        student_id=student_id,
        category=category,
        title=title,
        description=description,
        priority=priority.upper(),
        status="PENDING"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return {
        "success": True,
        "ticket_id": complaint.ticket_id,
        "status": complaint.status,
        "message": f"Complaint successfully filed with Ticket ID: {complaint.ticket_id}"
    }


def escalate_complaint_in_db(ticket_id: str, reason: str, db: Session) -> Dict[str, Any]:
    """Escalate a complaint ticket."""
    c = db.query(Complaint).filter(Complaint.ticket_id == ticket_id.strip()).first()
    if not c:
        return {"success": False, "message": f"Ticket '{ticket_id}' not found."}

    c.status = "ESCALATED"
    c.priority = "CRITICAL"
    escalation_entry = f"[Escalated via CampusAI Agent]: {reason}"
    if c.escalation_reason:
        c.escalation_reason += f"\n{escalation_entry}"
    else:
        c.escalation_reason = escalation_entry

    db.commit()
    return {
        "success": True,
        "ticket_id": c.ticket_id,
        "status": c.status,
        "message": f"Ticket {c.ticket_id} has been formally escalated to the Proctorial Board & Dean Office."
    }


def create_student_reminder_in_db(
    student_id: int,
    title: str,
    description: str,
    due_date: str,
    reminder_type: str,
    db: Session
) -> Dict[str, Any]:
    """Create a persistent student notification/reminder in the database."""
    rem = Notification(
        student_id=student_id,
        title=title,
        description=description,
        due_date=due_date,
        reminder_type=reminder_type.upper(),
        is_read=False,
        is_active=True
    )
    db.add(rem)
    db.commit()
    return {
        "success": True,
        "title": rem.title,
        "due_date": rem.due_date,
        "message": f"Reminder '{rem.title}' scheduled for {rem.due_date}."
    }

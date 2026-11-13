from sqlalchemy.orm import Session
from backend.app.models.entities import (
    User, StudentProfile, AcademicRecord, FeeRecord,
    Complaint, Announcement, Notification
)
from backend.app.services.auth_service import hash_password


def seed_initial_data(db: Session):
    """Seed sample campus records if the database is uninitialized."""
    # Check if admin already exists
    admin_exists = db.query(User).filter(User.email == "admin@campusai.edu").first()
    if admin_exists:
        return

    print("--- Seeding initial CampusAI demo records ---")

    # 1. Create Admin User
    admin = User(
        email="admin@campusai.edu",
        hashed_password=hash_password("admin123"),
        full_name="Dr. Sunita Verma (Dean Student Welfare)",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.flush()

    # 2. Create Demo Student User & Profile
    student_user = User(
        email="student@campusai.edu",
        hashed_password=hash_password("student123"),
        full_name="Aarav Sharma",
        role="student",
        is_active=True
    )
    db.add(student_user)
    db.flush()

    student_profile = StudentProfile(
        user_id=student_user.id,
        roll_number="2026CS1042",
        branch="Computer Science & Engineering",
        semester=6,
        section="A",
        cgpa=8.72,
        phone="+91-9876543210",
        hostel_resident=True,
        room_number="Hostel Block B - Room 304"
    )
    db.add(student_profile)
    db.flush()

    # 3. Create Academic Records (with one below 75% for realistic warning scenarios)
    academics = [
        AcademicRecord(
            student_id=student_profile.id,
            subject_code="CS601",
            subject_name="Machine Learning & AI",
            attendance_percentage=85.0,
            total_classes=40,
            attended_classes=34,
            internal_marks=27.5,
            semester=6
        ),
        AcademicRecord(
            student_id=student_profile.id,
            subject_code="CS602",
            subject_name="Distributed Cloud Systems",
            attendance_percentage=72.5,  # Alert: below 75%
            total_classes=40,
            attended_classes=29,
            internal_marks=23.0,
            semester=6
        ),
        AcademicRecord(
            student_id=student_profile.id,
            subject_code="CS603",
            subject_name="Compiler Design",
            attendance_percentage=90.0,
            total_classes=40,
            attended_classes=36,
            internal_marks=28.0,
            semester=6
        ),
        AcademicRecord(
            student_id=student_profile.id,
            subject_code="CS604",
            subject_name="Information & Network Security",
            attendance_percentage=78.0,
            total_classes=40,
            attended_classes=31,
            internal_marks=25.0,
            semester=6
        )
    ]
    db.add_all(academics)

    # 4. Create Fee Records
    fee_records = [
        FeeRecord(
            student_id=student_profile.id,
            semester=6,
            total_amount=65000.0,
            paid_amount=45000.0,
            due_amount=20000.0,
            due_date="15 Dec 2026",
            status="PARTIAL",
            payment_ref="TXN-ERP-98231"
        ),
        FeeRecord(
            student_id=student_profile.id,
            semester=5,
            total_amount=65000.0,
            paid_amount=65000.0,
            due_amount=0.0,
            due_date="10 Jun 2026",
            status="PAID",
            payment_ref="TXN-ERP-41092"
        )
    ]
    db.add_all(fee_records)

    # 5. Create Initial Complaints
    complaints = [
        Complaint(
            ticket_id="CMP-2026-1001",
            student_id=student_profile.id,
            category="Wi-Fi",
            title="Hostel Block B 3rd Floor Wi-Fi drops frequently in evenings",
            description="The Wi-Fi access point in corridor 3 disconnected continuously between 8 PM and 11 PM, impeding assignment submissions.",
            priority="HIGH",
            status="IN_REVIEW"
        ),
        Complaint(
            ticket_id="CMP-2026-0940",
            student_id=student_profile.id,
            category="Academic",
            title="Correction of lecture count for CS602 on 14th Oct",
            description="Medical leave certificate submitted to mentor was not reflected in the ERP attendance total.",
            priority="MEDIUM",
            status="RESOLVED",
            escalation_reason="Resolved by Class Mentor Prof. Gupta on 20 Oct 2026."
        )
    ]
    db.add_all(complaints)

    # 6. Create Campus Announcements
    announcements = [
        Announcement(
            title="Even Semester Mid-Term Examination Datesheet",
            category="Exams",
            content="Mid-Term examinations for all B.Tech 6th Semester programs commence from 25th November 2026. Official schedules and seating plans are published on the Examination Cell notice board.",
            published_date="04 Nov 2026",
            is_urgent=True,
            target_branch="ALL"
        ),
        Announcement(
            title="TCS Digital Campus Recruitment Drive 2026",
            category="Placements",
            content="TCS Digital recruitment drive registration is open for CS/IT students with CGPA >= 7.5. Register on the T&P portal before 20th November 2026.",
            published_date="02 Nov 2026",
            is_urgent=False,
            target_branch="CSE"
        ),
        Announcement(
            title="UP Post-Matric Scholarship Hard Copy Submission",
            category="Scholarship",
            content="All scholarship applicants must deposit signed verification forms along with income certificate copies at Counter 4 before 30th November 2026.",
            published_date="01 Nov 2026",
            is_urgent=True,
            target_branch="ALL"
        )
    ]
    db.add_all(announcements)

    # 7. Create Pending Student Reminders
    notifications = [
        Notification(
            student_id=student_profile.id,
            title="Fee Balance Payment Due",
            description="Semester 6 balance of ₹20,000 must be cleared before 15 Dec 2026 to avoid late fees.",
            due_date="15 Dec 2026",
            reminder_type="FEE",
            is_read=False,
            is_active=True
        ),
        Notification(
            student_id=student_profile.id,
            title="CS602 Attendance Advisory",
            description="Your current attendance in CS602 is 72.5% (below mandatory 75% threshold). Please attend upcoming tutorial classes.",
            due_date="20 Nov 2026",
            reminder_type="EXAM",
            is_read=False,
            is_active=True
        )
    ]
    db.add_all(notifications)

    db.commit()
    print("--- Initial CampusAI database seed complete! ---")

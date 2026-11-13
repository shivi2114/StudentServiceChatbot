import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.entities import User, StudentProfile, AcademicRecord, FeeRecord
from backend.app.schemas.all_schemas import LoginRequest, Token, UserResponse, StudentProfileResponse, UserCreate
from backend.app.services.auth_service import (
    verify_password, create_access_token, get_current_user, hash_password
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with simple, friction-free login (accepts username, email, or ID)."""
    raw_input = request.email.strip().lower()
    if not raw_input:
        raw_input = "student"

    # Allow entering just "shivi", "admin", "student", or full email
    if "@" not in raw_input:
        email_clean = f"{raw_input}@campusai.edu"
    else:
        email_clean = raw_input

    user = db.query(User).filter(User.email == email_clean).first()
    
    # If not found by email, try matching by name
    if not user:
        user = db.query(User).filter(User.full_name.ilike(f"%{raw_input}%")).first()

    pwd = request.password.strip() if request.password and request.password.strip() else "123456"

    if not user:
        # Seamless onboarding: auto-create student or admin profile
        role = "admin" if ("admin" in raw_input or "dean" in raw_input) else "student"
        raw_name = raw_input.split("@")[0].replace(".", " ").replace("_", " ").title()
        
        user = User(
            email=email_clean,
            hashed_password=hash_password(pwd),
            full_name=raw_name or "Campus User",
            role=role,
            is_active=True
        )
        db.add(user)
        db.flush()

        if role == "student":
            roll = f"2026CS{random.randint(1000, 9999)}"
            profile = StudentProfile(
                user_id=user.id,
                roll_number=roll,
                branch="Computer Science & Engineering",
                semester=6,
                section="A",
                cgpa=8.65,
                phone="+91-9876543210",
                hostel_resident=True,
                room_number="Hostel Block B - Room 204"
            )
            db.add(profile)
            db.flush()

            academics = [
                AcademicRecord(
                    student_id=profile.id,
                    subject_code="CS601",
                    subject_name="Machine Learning & AI",
                    attendance_percentage=85.0,
                    total_classes=40,
                    attended_classes=34,
                    internal_marks=28.0,
                    semester=6
                ),
                AcademicRecord(
                    student_id=profile.id,
                    subject_code="CS602",
                    subject_name="Distributed Cloud Systems",
                    attendance_percentage=78.0,
                    total_classes=40,
                    attended_classes=31,
                    internal_marks=25.0,
                    semester=6
                ),
                AcademicRecord(
                    student_id=profile.id,
                    subject_code="CS603",
                    subject_name="Compiler Design",
                    attendance_percentage=88.0,
                    total_classes=40,
                    attended_classes=35,
                    internal_marks=27.0,
                    semester=6
                ),
                AcademicRecord(
                    student_id=profile.id,
                    subject_code="CS604",
                    subject_name="Information & Network Security",
                    attendance_percentage=82.0,
                    total_classes=40,
                    attended_classes=33,
                    internal_marks=26.0,
                    semester=6
                )
            ]
            db.add_all(academics)

            fee_records = [
                FeeRecord(
                    student_id=profile.id,
                    semester=6,
                    total_amount=65000.0,
                    paid_amount=45000.0,
                    due_amount=20000.0,
                    due_date="15 Dec 2026",
                    status="PARTIAL",
                    payment_ref="TXN-ERP-78219"
                ),
                FeeRecord(
                    student_id=profile.id,
                    semester=5,
                    total_amount=65000.0,
                    paid_amount=65000.0,
                    due_amount=0.0,
                    due_date="10 Jun 2026",
                    status="PAID",
                    payment_ref="TXN-ERP-33104"
                )
            ]
            db.add_all(fee_records)

        db.commit()
        db.refresh(user)

    else:
        # User exists: always keep access seamless without blocking passwords
        if pwd:
            user.hashed_password = hash_password(pwd)
            db.commit()

    if not user.is_active:
        user.is_active = True
        db.commit()

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )


@router.post("/register", response_model=Token)
def register(request: UserCreate, db: Session = Depends(get_db)):
    """Register a new student or admin user."""
    email_clean = request.email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    role = request.role if request.role in ["student", "admin"] else "student"
    user = User(
        email=email_clean,
        hashed_password=hash_password(request.password),
        full_name=request.full_name.strip() or "Campus User",
        role=role,
        is_active=True
    )
    db.add(user)
    db.flush()

    if role == "student":
        roll = f"2026CS{random.randint(1000, 9999)}"
        profile = StudentProfile(
            user_id=user.id,
            roll_number=roll,
            branch="Computer Science & Engineering",
            semester=6,
            section="A",
            cgpa=8.50,
            phone="+91-9876543210",
            hostel_resident=True,
            room_number="Hostel Block B - Room 204"
        )
        db.add(profile)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )


@router.get("/me")
def get_current_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get authenticated user info and associated student profile."""
    profile_data = None
    if current_user.role == "student":
        student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if student:
            profile_data = StudentProfileResponse(
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

    return {
        "user": UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active
        ),
        "student_profile": profile_data
    }

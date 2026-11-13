from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="student", nullable=False)  # "student" or "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    branch = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String(10), nullable=True, default="A")
    cgpa = Column(Float, nullable=False, default=8.0)
    phone = Column(String(20), nullable=True)
    hostel_resident = Column(Boolean, default=False)
    room_number = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    academic_records = relationship("AcademicRecord", back_populates="student", cascade="all, delete")
    fee_records = relationship("FeeRecord", back_populates="student", cascade="all, delete")
    complaints = relationship("Complaint", back_populates="student", cascade="all, delete")
    notifications = relationship("Notification", back_populates="student", cascade="all, delete")


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    subject_code = Column(String(50), nullable=False)
    subject_name = Column(String(150), nullable=False)
    attendance_percentage = Column(Float, nullable=False)
    total_classes = Column(Integer, default=40)
    attended_classes = Column(Integer, default=32)
    internal_marks = Column(Float, default=24.0)
    semester = Column(Integer, nullable=False)

    student = relationship("StudentProfile", back_populates="academic_records")


class FeeRecord(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, nullable=False, default=0.0)
    due_amount = Column(Float, nullable=False, default=0.0)
    due_date = Column(String(50), nullable=False)
    status = Column(String(50), default="PENDING")  # "PAID", "PARTIAL", "PENDING"
    payment_ref = Column(String(100), nullable=True)

    student = relationship("StudentProfile", back_populates="fee_records")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)  # Academic, Hostel, Wi-Fi, Library, Accounts, General
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="PENDING")   # PENDING, IN_REVIEW, RESOLVED, ESCALATED
    escalation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    student = relationship("StudentProfile", back_populates="complaints")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Academics, Placements, Exams, General
    content = Column(Text, nullable=False)
    published_date = Column(String(50), nullable=False)
    is_urgent = Column(Boolean, default=False)
    target_branch = Column(String(100), default="ALL")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(String(100), nullable=True)
    reminder_type = Column(String(50), default="GENERAL")  # EXAM, FEE, ASSIGNMENT, GENERAL
    is_read = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    student = relationship("StudentProfile", back_populates="notifications")


class DocumentRecord(Base):
    __tablename__ = "document_records"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Regulations, Fees, Exams, Placements, Hostel
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    chunk_count = Column(Integer, default=0)
    uploaded_by = Column(String(255), default="admin")
    created_at = Column(DateTime, default=utc_now)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Campus Inquiry")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_name = Column(String(100), nullable=True)  # Orchestrator, Academic, Fee, Complaint, etc.
    source = Column(String(100), nullable=True)      # RAG, Database, Verified_KB, LLM
    metadata_json = Column(Text, nullable=True)      # JSON string for citations, actions, etc.
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ChatSession", back_populates="messages")

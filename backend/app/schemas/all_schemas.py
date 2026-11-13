from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ==========================================
# Authentication Schemas
# ==========================================

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str
    email: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "student"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================
# Academic & Student Schemas
# ==========================================

class AcademicRecordResponse(BaseModel):
    id: int
    subject_code: str
    subject_name: str
    attendance_percentage: float
    total_classes: int
    attended_classes: int
    internal_marks: float
    semester: int

    class Config:
        from_attributes = True


class FeeRecordResponse(BaseModel):
    id: int
    semester: int
    total_amount: float
    paid_amount: float
    due_amount: float
    due_date: str
    status: str
    payment_ref: Optional[str] = None

    class Config:
        from_attributes = True


class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    roll_number: str
    branch: str
    semester: int
    section: Optional[str] = "A"
    cgpa: float
    phone: Optional[str] = None
    hostel_resident: bool
    room_number: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# Complaint Schemas
# ==========================================

class ComplaintCreate(BaseModel):
    category: str = Field(..., description="Category: Academic, Hostel, Wi-Fi, Library, Accounts, General")
    title: str = Field(..., max_length=200)
    description: str
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    escalation_reason: Optional[str] = None


class ComplaintEscalate(BaseModel):
    reason: str


class ComplaintResponse(BaseModel):
    id: int
    ticket_id: str
    student_id: int
    category: str
    title: str
    description: str
    priority: str
    status: str
    escalation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==========================================
# Announcement & Notification Schemas
# ==========================================

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    category: str
    content: str
    published_date: str
    is_urgent: bool
    target_branch: str

    class Config:
        from_attributes = True


class AnnouncementCreate(BaseModel):
    title: str
    category: str
    content: str
    published_date: str
    is_urgent: bool = False
    target_branch: str = "ALL"


class NotificationResponse(BaseModel):
    id: int
    student_id: int
    title: str
    description: str
    due_date: Optional[str] = None
    reminder_type: str
    is_read: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    title: str
    description: str
    due_date: Optional[str] = None
    reminder_type: str = "GENERAL"


# ==========================================
# Document & RAG Schemas
# ==========================================

class DocumentRecordResponse(BaseModel):
    id: int
    title: str
    category: str
    filename: str
    chunk_count: int
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class Citation(BaseModel):
    document_title: str
    source_file: str
    page_number: Optional[int] = 1
    snippet: str
    relevance_score: Optional[float] = None


# ==========================================
# Chat & Multi-Agent Schemas
# ==========================================

class ChatMessageSchema(BaseModel):
    id: Optional[int] = None
    role: str
    content: str
    agent_name: Optional[str] = None
    source: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[ChatMessageSchema] = []

    class Config:
        from_attributes = True


class ActionConfirmation(BaseModel):
    action_type: str  # e.g. "submit_complaint", "create_reminder", "initiate_fee_payment"
    action_title: str
    details: Dict[str, Any]
    requires_approval: bool = True


class ChatQueryRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "en"  # "en" or "hi"
    confirmed_action: Optional[Dict[str, Any]] = None  # Passed when user approves an action


class ChatQueryResponse(BaseModel):
    session_id: str
    answer: str
    agent_name: str
    source: str  # "rag", "database", "verified_kb", "orchestrator", "action_required"
    citations: List[Citation] = []
    action_required: Optional[ActionConfirmation] = None
    office_referral: Optional[Dict[str, str]] = None
    follow_up_suggestions: List[str] = []


# ==========================================
# Full Dashboard Aggregate
# ==========================================

class StudentFullDashboardResponse(BaseModel):
    profile: StudentProfileResponse
    academics: List[AcademicRecordResponse]
    overall_attendance: float
    fees: List[FeeRecordResponse]
    total_due: float
    recent_complaints: List[ComplaintResponse]
    announcements: List[AnnouncementResponse]
    notifications: List[NotificationResponse]

import os
from pathlib import Path
import pickle
import re
import pandas as pd

from utils import clean_text
from groq_chat import ask_groq

BASE_DIR = Path(__file__).resolve().parent

# ==========================
# Load ML Model & Artifacts
# ==========================

with open(BASE_DIR / "model.pkl", "rb") as f:
    model = pickle.load(f)

with open(BASE_DIR / "vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

with open(BASE_DIR / "label_encoder.pkl", "rb") as f:
    encoder = pickle.load(f)

# ==========================
# Load & Cache Dataset
# ==========================

df = pd.read_csv(BASE_DIR / "student_services_dataset_17000_plus.csv")
INTENT_ANSWERS = df.groupby("intent")["answer"].first().to_dict()

# ==========================
# Campus Directory & Routing
# ==========================

SERVICE_DIRECTORY = {
    "admission": {"name": "Admission", "office": "Admission Cell", "contact": "Admission Portal & Campus Desk"},
    "eligibility": {"name": "Eligibility", "office": "Admission Cell", "contact": "Official Regulations Guide"},
    "documents": {"name": "Required Documents", "office": "Admission Cell", "contact": "Document Verification Counter"},
    "fees": {"name": "Fees Payment", "office": "Accounts Office", "contact": "ERP Portal / Accounts Counter"},
    "fee_refund": {"name": "Fee Refund", "office": "Accounts Office", "contact": "Accounts Office Counter"},
    "hostel": {"name": "Hostel Allotment", "office": "Hostel Office", "contact": "Hostel Warden Office"},
    "hostel_fee": {"name": "Hostel Fee", "office": "Hostel Office", "contact": "Hostel Administration Counter"},
    "mess": {"name": "Hostel Mess", "office": "Hostel Office", "contact": "Hostel Notice Board"},
    "library": {"name": "Central Library", "office": "Central Library", "contact": "Circulation Counter (9:00 AM - 5:00 PM)"},
    "book_issue": {"name": "Book Issue & Return", "office": "Central Library", "contact": "Library Helpdesk"},
    "exam_schedule": {"name": "Examination Schedule", "office": "Examination Cell", "contact": "University Portal / Exam Notice Board"},
    "result": {"name": "Semester Results", "office": "Examination Cell", "contact": "University Portal"},
    "revaluation": {"name": "Result Revaluation", "office": "Examination Cell", "contact": "Examination Cell Counter"},
    "back_paper": {"name": "Back Paper Registration", "office": "Examination Cell", "contact": "Examination Cell Desk"},
    "attendance": {"name": "Attendance Requirement", "office": "Academic Department", "contact": "ERP Portal / Class Mentor"},
    "leave": {"name": "Leave Application", "office": "Academic Department", "contact": "Mentor / HOD Office"},
    "scholarship": {"name": "Scholarships", "office": "Scholarship Cell", "contact": "Student Welfare Section"},
    "placement": {"name": "Campus Placements", "office": "Training & Placement Cell", "contact": "T&P Desk"},
    "internship": {"name": "Internships", "office": "Training & Placement Cell", "contact": "Placement Coordinator"},
    "training": {"name": "Skill Training", "office": "Training & Placement Cell", "contact": "Skill Development Cell"},
    "faculty": {"name": "Faculty Information", "office": "Department Webpage", "contact": "Department Faculty Directory"},
    "hod": {"name": "Head of Department", "office": "Department HOD Office", "contact": "HOD Office Hours"},
    "timetable": {"name": "Class Timetable", "office": "Department Office", "contact": "Department Notice Board / ERP"},
    "academic_calendar": {"name": "Academic Calendar", "office": "Academic Affairs", "contact": "Academic Portal & Calendar"},
    "holiday": {"name": "Holiday List", "office": "Academic Affairs", "contact": "Official Academic Calendar"},
    "id_card": {"name": "Student ID Card", "office": "Student Affairs", "contact": "Student Affairs Counter"},
    "bonafide": {"name": "Bonafide Certificate", "office": "Administration Office", "contact": "Student Section Desk"},
    "migration": {"name": "Migration Certificate", "office": "Administration Office", "contact": "University Procedures Desk"},
    "character_certificate": {"name": "Character Certificate", "office": "Administration Office", "contact": "Administration Counter"},
    "transport": {"name": "Campus Transport", "office": "Transport Office", "contact": "Transport Desk"},
    "wifi": {"name": "Campus Wi-Fi", "office": "IT Support Desk", "contact": "Campus Network Cell"},
    "erp": {"name": "Student ERP Portal", "office": "IT Support / ERP Cell", "contact": "ERP Portal Desk"},
    "login": {"name": "Portal Login Credentials", "office": "IT Support Desk", "contact": "IT Helpdesk"},
    "password_reset": {"name": "Password Reset", "office": "IT Support Desk", "contact": "ERP Portal / IT Desk"},
    "medical": {"name": "Medical Assistance", "office": "Campus Health Center", "contact": "Medical Room (Working Hours)"},
    "sports": {"name": "Sports Facilities", "office": "Sports Department", "contact": "Sports Complex Office"},
    "clubs": {"name": "Student Clubs", "office": "Student Activity Council", "contact": "Club Coordinators"},
    "canteen": {"name": "Campus Canteen", "office": "Campus Canteen", "contact": "Main Canteen Building"},
    "anti_ragging": {"name": "Anti-Ragging Helpline", "office": "Anti-Ragging Committee", "contact": "Proctorial Board / Helpline"},
    "complaint": {"name": "Student Grievance", "office": "Grievance Redressal Cell", "contact": "Grievance Portal / Desk"},
    "grievance": {"name": "Grievance Redressal", "office": "Grievance Redressal Cell", "contact": "Confidential Grievance Desk"},
    "nss": {"name": "NSS Enrolment", "office": "NSS Cell", "contact": "NSS Program Officer"},
    "ncc": {"name": "NCC Enrolment", "office": "NCC Office", "contact": "NCC Unit Office"},
    "events": {"name": "Campus Events", "office": "Student Affairs", "contact": "College Notice Board & Website"},
    "project": {"name": "Student Projects", "office": "Department Project Cell", "contact": "Project Guide / Coordinator"},
    "lab": {"name": "Laboratory Schedules", "office": "Department Labs", "contact": "Lab Technician / Department Notice"},
    "syllabus": {"name": "Course Syllabus", "office": "Academic Affairs", "contact": "University Website"},
    "contact": {"name": "General Enquiries", "office": "College Reception", "contact": "Main Reception Desk"}
}

GREETINGS = {
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
    "greetings", "namaste", "hi there", "hello there"
}

GRATITUDE = {
    "thanks", "thank you", "thank you so much", "thx", "appreciate it"
}

HELP_TRIGGERS = {
    "help", "what can you do", "menu", "options", "commands", "topics"
}


def _check_conversational_intents(text: str) -> str | None:
    """Return an instant response for conversational greetings or pleasantries."""
    normalized = re.sub(r"[^\w\s]", "", text.strip().lower())
    if normalized in GREETINGS:
        return (
            "Hello! I am your Student Services Assistant. You can ask me practical questions about admissions, "
            "fees, hostel rules, library hours, exam schedules, and department support contacts. "
            "What can I help you with today?"
        )
    if normalized in GRATITUDE:
        return "You're welcome! Let me know if you need help with any other student services."
    if normalized in HELP_TRIGGERS:
        return (
            "I can assist with practical student inquiries across campus:\n\n"
            "- **Admissions & Documents**: Eligibility criteria and application requirements.\n"
            "- **Fees & Accounts**: Payment methods, ERP online fee portal, and refunds.\n"
            "- **Academics & Attendance**: Minimum 75% attendance rule, timetable, and leave.\n"
            "- **Examinations**: Exam schedules, semester results, back paper, and revaluation.\n"
            "- **Hostel & Facilities**: Allotment rules, mess timings, library hours, and Wi-Fi.\n"
            "- **Campus Offices**: Direct guidance to the Accounts Office, Library, IT Support, and Reception.\n\n"
            "Feel free to type your question below or click any example question."
        )
    return None


def get_detailed_response(question: str, history: list = None) -> dict:
    """
    Generate a detailed response dictionary containing:
    - answer (str)
    - source ('verified_kb', 'ai_assistant', 'conversational', 'validation', 'error')
    - intent (str | None)
    - confidence (float)
    - office (str | None)
    - contact (str | None)
    """
    try:
        # Input validation
        if not question or not question.strip():
            return {
                "answer": "Please type a question about campus services, courses, fees, or facilities.",
                "source": "validation",
                "intent": None,
                "confidence": 0.0,
                "office": None,
                "contact": None
            }

        raw_query = question.strip()

        # Check for alphanumeric characters
        if not re.search(r"[a-zA-Z0-9]", raw_query):
            return {
                "answer": "Please enter a valid question about campus student services.",
                "source": "validation",
                "intent": None,
                "confidence": 0.0,
                "office": None,
                "contact": None
            }

        # Quick conversational checks
        conversational_resp = _check_conversational_intents(raw_query)
        if conversational_resp:
            return {
                "answer": conversational_resp,
                "source": "conversational",
                "intent": "conversational",
                "confidence": 1.0,
                "office": None,
                "contact": None
            }

        # Clean user input for ML model
        clean = clean_text(raw_query)
        if not clean:
            # If after cleaning nothing remains, query Groq with context
            ai_reply = ask_groq(raw_query, history=history)
            return {
                "answer": ai_reply,
                "source": "ai_assistant",
                "intent": None,
                "confidence": 0.0,
                "office": None,
                "contact": None
            }

        # Convert to TF-IDF vector
        vector = vectorizer.transform([clean])

        # Predict intent and confidence
        prediction = model.predict(vector)
        intent = encoder.inverse_transform(prediction)[0]
        confidence = float(model.predict_proba(vector).max())

        print(f"Predicted Intent: {intent} (Confidence: {confidence:.2f})")

        # High confidence match (>= 0.70) in verified dataset
        if confidence >= 0.70 and intent in INTENT_ANSWERS:
            canonical_answer = INTENT_ANSWERS[intent]
            routing = SERVICE_DIRECTORY.get(intent)
            return {
                "answer": canonical_answer,
                "source": "verified_kb",
                "intent": intent,
                "confidence": confidence,
                "office": routing["office"] if routing else None,
                "contact": routing["contact"] if routing else None
            }

        # Low confidence (< 0.70): Ask Groq AI with grounded prompt and history
        groq_reply = ask_groq(raw_query, history=history)
        return {
            "answer": groq_reply,
            "source": "ai_assistant",
            "intent": intent,
            "confidence": confidence,
            "office": None,
            "contact": None
        }

    except Exception as e:
        print(f"Error in get_detailed_response: {e}")
        return {
            "answer": "I could not retrieve that information right now. For official guidance, please contact the College Reception or your department coordinator.",
            "source": "error",
            "intent": None,
            "confidence": 0.0,
            "office": "College Reception",
            "contact": "Main Administration Block"
        }


def get_response(question: str, history: list = None) -> str:
    """
    Generate an authoritative string response to a student query.
    Backward-compatible wrapper around get_detailed_response.
    """
    result = get_detailed_response(question, history=history)
    answer = result["answer"]
    if result.get("office"):
        answer += f"\n\n**Campus Office:** {result['office']} ({result['contact']})"
    return answer

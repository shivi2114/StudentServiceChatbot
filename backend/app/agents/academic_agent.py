from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.state import CampusAgentState
from backend.app.rag.vector_store import rag_store
from backend.app.tools.campus_tools import get_student_academic_summary, lookup_campus_office
from backend.app.services.llm_service import call_llm


def run_academic_agent(state: CampusAgentState, db: Session) -> Dict[str, Any]:
    """Specialized Academic Agent handling attendance, exams, syllabus, and results."""
    query = state["user_query"]
    student_id = state.get("student_id")
    student_profile = state.get("student_profile") or {}
    language = state.get("language", "en")

    # 1. RAG search for relevant institutional regulations
    citations = rag_store.search(query, top_k=3)

    # 2. Check if student is asking about their personal attendance / records
    personal_academic_context = ""
    is_personal_query = any(w in query.lower() for w in ["my attendance", "my marks", "my courses", "am i eligible", "my subjects", "am i detained"])
    
    if student_id and is_personal_query:
        acad_summary = get_student_academic_summary(student_id, db)
        if acad_summary["found"]:
            courses_str = ", ".join([f"{c['subject_code']} ({c['subject_name']}): {c['attendance']}%" for c in acad_summary["courses"]])
            personal_academic_context = (
                f"\nStudent Verified Academic Records:\n"
                f"- Average Attendance: {acad_summary['average_attendance']}%\n"
                f"- Course Details: {courses_str}\n"
            )
            if acad_summary["low_attendance_warnings"]:
                warns = ", ".join([f"{w['subject']} ({w['attendance']}%, deficit: {w['deficit']}%)" for w in acad_summary["low_attendance_warnings"]])
                personal_academic_context += f"- WARNING: The following subjects are below the mandatory 75% threshold: {warns}\n"

    # Build RAG excerpts context
    rag_context = "\n\n".join([f"[{c['document_title']} - Page {c['page_number']}]:\n{c['snippet']}" for c in citations])

    system_instruction = (
        "You are the Academic Specialist Agent for CampusAI. "
        "Your role is to assist students with attendance rules (75% mandatory rule, medical condonation up to 15%), "
        "examination schedules, passing criteria (35% in end-sem, 40% aggregate), syllabus, and back-paper policies. "
        "Ground your answer strictly on the provided Institutional Documents and Student Records below. "
        "Do not invent policies or fake dates. If answering in Hindi, use natural, clear Hinglish or Hindi."
    )

    prompt = (
        f"Institutional Documents Excerpts:\n{rag_context}\n"
        f"{personal_academic_context}\n"
        f"Student Query: {query}\n"
        f"Language: {language}\n"
        "Provide a helpful, precise, grounded response with exact rules."
    )

    llm_reply = call_llm(prompt, system_instruction=system_instruction, history=state.get("messages", []))

    # Follow up suggestions
    follow_ups = [
        "What is the medical condonation procedure for attendance?",
        "How do I apply for semester exam revaluation?",
        "What are the passing marks for end-term exams?"
    ]

    office = lookup_campus_office("exam_schedule") or {
        "office": "Examination Cell & Academic Department",
        "contact": "Counter 3 (Ground Floor, Admin Block)"
    }

    return {
        "final_response": llm_reply,
        "current_agent": "Academic Agent",
        "source_type": "rag" if citations else "database",
        "citations": citations,
        "office_referral": office,
        "follow_up_suggestions": follow_ups
    }

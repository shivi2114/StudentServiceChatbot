from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.state import CampusAgentState
from backend.app.rag.vector_store import rag_store
from backend.app.tools.campus_tools import lookup_campus_office
from backend.app.services.llm_service import call_llm


def run_scholarship_agent(state: CampusAgentState, db: Session) -> Dict[str, Any]:
    """Specialized Scholarship Agent matching verified schemes and application deadlines."""
    query = state["user_query"]
    student_profile = state.get("student_profile") or {}
    language = state.get("language", "en")

    citations = rag_store.search(query, top_k=3)
    rag_context = "\n\n".join([f"[{c['document_title']} - Page {c['page_number']}]:\n{c['snippet']}" for c in citations])

    profile_context = ""
    if student_profile:
        cgpa = student_profile.get("cgpa", 0.0)
        branch = student_profile.get("branch", "Engineering")
        profile_context = (
            f"\nStudent Profile:\n"
            f"- Branch: {branch}\n"
            f"- Current CGPA: {cgpa}\n"
        )
        if cgpa >= 8.75:
            profile_context += "- High Merit Status: Student qualifies for Institute Merit-cum-Means (MCM) Tuition Fee Waiver.\n"

    system_instruction = (
        "You are the Scholarship Specialist Agent for CampusAI. "
        "Your role is to guide students on verified institutional and government scholarships: "
        "1. UP Post-Matric Scholarship (Income limit INR 2-2.5 Lakhs, 75% mandatory biometric attendance, deadline 30th Nov 2026 at Window 4). "
        "2. AICTE Pragati Scholarship for Girls (INR 50,000/year, NSP Portal deadline 15th Dec 2026). "
        "3. Campus Merit-cum-Means (MCM) Fellowship (CGPA >= 8.75 yields 25% fee waiver, CGPA >= 9.20 yields 50% waiver). "
        "Match the student's profile against these criteria. Never invent unverified schemes or fraudulent links."
    )

    prompt = (
        f"Verified Scholarship Guidelines:\n{rag_context}\n"
        f"{profile_context}\n"
        f"Student Query: {query}\n"
        f"Language: {language}\n"
        "Provide a clear, detailed, and encouraging scholarship guide."
    )

    llm_reply = call_llm(prompt, system_instruction=system_instruction, history=state.get("messages", []))

    follow_ups = [
        "What documents are needed for UP Post-Matric Scholarship?",
        "How do I apply for the Merit-cum-Means fee waiver?",
        "What is the last date to submit scholarship hard copies?"
    ]

    office = lookup_campus_office("scholarship") or {
        "office": "Scholarship Cell & Student Welfare Desk",
        "contact": "Counter 4, Admin Block (11:00 AM - 3:00 PM)"
    }

    return {
        "final_response": llm_reply,
        "current_agent": "Scholarship Agent",
        "source_type": "rag",
        "citations": citations,
        "office_referral": office,
        "follow_up_suggestions": follow_ups
    }

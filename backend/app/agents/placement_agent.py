from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.state import CampusAgentState
from backend.app.rag.vector_store import rag_store
from backend.app.tools.campus_tools import lookup_campus_office
from backend.app.services.llm_service import call_llm


def run_placement_agent(state: CampusAgentState, db: Session) -> Dict[str, Any]:
    """Specialized Placement and Career Agent for campus recruitment and internships."""
    query = state["user_query"]
    student_profile = state.get("student_profile") or {}
    language = state.get("language", "en")

    citations = rag_store.search(query, top_k=3)
    rag_context = "\n\n".join([f"[{c['document_title']} - Page {c['page_number']}]:\n{c['snippet']}" for c in citations])

    profile_context = ""
    if student_profile:
        cgpa = student_profile.get("cgpa", 0.0)
        branch = student_profile.get("branch", "Engineering")
        sem = student_profile.get("semester", 6)
        profile_context = (
            f"\nStudent Academic Standing:\n"
            f"- Branch: {branch}, Semester: {sem}\n"
            f"- CGPA: {cgpa}\n"
        )
        if cgpa >= 7.50:
            profile_context += "- Tier 1 Qualification: Student is fully eligible for Tier 1 Dream Recruiters (CTC > 10 LPA).\n"
        elif cgpa >= 6.50:
            profile_context += "- Tier 2 Qualification: Student is eligible for Tier 2 Core Recruiters (CTC 6-10 LPA).\n"

    system_instruction = (
        "You are the Placement & Career Specialist Agent for CampusAI. "
        "Your role is to guide students on campus placement policy: "
        "- Placement Tiers: Tier 1 (Dream > 10 LPA, CGPA >= 7.5), Tier 2 (6-10 LPA, CGPA >= 6.5), Tier 3 (Mass 3.5-5.5 LPA, CGPA >= 6.0). "
        "- One Student, One Job Policy and Super Dream Upgradation (CTC >= 14 LPA). "
        "- 8th Semester Industry Internship NOC requirements. "
        "- Upcoming drives: TCS Digital (1st Dec 2026), Cognizant GenC Next (10th Dec 2026). "
        "Personalize advice using the student's CGPA and branch."
    )

    prompt = (
        f"Verified Placement Policies:\n{rag_context}\n"
        f"{profile_context}\n"
        f"Student Query: {query}\n"
        f"Language: {language}\n"
        "Provide a strategic, grounded, and empowering placement briefing."
    )

    llm_reply = call_llm(prompt, system_instruction=system_instruction, history=state.get("messages", []))

    follow_ups = [
        "What are the upcoming placement drives this semester?",
        "How do I obtain a No Objection Certificate (NOC) for internships?",
        "What is the One Student, One Job policy?"
    ]

    office = lookup_campus_office("placement") or {
        "office": "Training & Placement Cell (T&P)",
        "contact": "Placement Complex, Block C, Ground Floor (Dr. R. K. Saxena)"
    }

    return {
        "final_response": llm_reply,
        "current_agent": "Placement & Career Agent",
        "source_type": "rag",
        "citations": citations,
        "office_referral": office,
        "follow_up_suggestions": follow_ups
    }

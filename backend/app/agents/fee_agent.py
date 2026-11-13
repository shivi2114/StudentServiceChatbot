from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.state import CampusAgentState
from backend.app.rag.vector_store import rag_store
from backend.app.tools.campus_tools import get_student_fee_summary, lookup_campus_office
from backend.app.services.llm_service import call_llm


def run_fee_agent(state: CampusAgentState, db: Session) -> Dict[str, Any]:
    """Specialized Admission and Fee Agent handling fee structure, ERP payments, and dues."""
    query = state["user_query"]
    student_id = state.get("student_id")
    language = state.get("language", "en")

    # 1. RAG search in fee policy and deadlines
    citations = rag_store.search(query, top_k=3)

    # 2. Check if student is asking about their personal dues / fee status
    personal_fee_context = ""
    is_personal_fee_query = any(w in query.lower() for w in ["my fee", "my dues", "how much do i owe", "have i paid", "my payment", "pending balance", "receipt"])

    if student_id and is_personal_fee_query:
        fee_summary = get_student_fee_summary(student_id, db)
        if fee_summary["found"]:
            records_str = "\n".join([
                f"- Semester {r['semester']}: Total INR {r['total_amount']:.2f}, Paid INR {r['paid_amount']:.2f}, Due INR {r['due_amount']:.2f} (Status: {r['status']}, Due Date: {r['due_date']}, Ref: {r['payment_ref']})"
                for r in fee_summary["records"]
            ])
            personal_fee_context = (
                f"\nStudent Verified Fee Ledger:\n"
                f"{records_str}\n"
                f"Total Outstanding Due: INR {fee_summary['total_due_amount']:.2f}\n"
            )

    rag_context = "\n\n".join([f"[{c['document_title']} - Page {c['page_number']}]:\n{c['snippet']}" for c in citations])

    system_instruction = (
        "You are the Admission and Fee Specialist Agent for CampusAI. "
        "Your role is to explain official tuition fees (INR 65,000/sem), hostel fees (INR 34,000 - 42,000/sem), "
        "payment procedures (Online ERP, UPI/NetBanking, No Cash), late fees (INR 100/day after 15th Dec 2026), "
        "and refund policies. Ground your response in the institutional guidelines and real fee ledger below. "
        "Do not invent fake deadlines or account numbers."
    )

    prompt = (
        f"Institutional Documents Excerpts:\n{rag_context}\n"
        f"{personal_fee_context}\n"
        f"Student Query: {query}\n"
        f"Language: {language}\n"
        "Provide a clear, authoritative, student-friendly fee answer."
    )

    llm_reply = call_llm(prompt, system_instruction=system_instruction, history=state.get("messages", []))

    follow_ups = [
        "What are the payment deadlines and late fee fines?",
        "How do I pay fees online through the Student ERP portal?",
        "What is the fee refund policy if a student withdraws?"
    ]

    office = lookup_campus_office("fees") or {
        "office": "Accounts Office",
        "contact": "Admin Block, Windows 1-4 (9:30 AM - 3:30 PM)"
    }

    return {
        "final_response": llm_reply,
        "current_agent": "Admission & Fee Agent",
        "source_type": "database" if personal_fee_context else "rag",
        "citations": citations,
        "office_referral": office,
        "follow_up_suggestions": follow_ups
    }

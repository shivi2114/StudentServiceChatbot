import re
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.state import CampusAgentState
from backend.app.tools.campus_tools import (
    get_complaint_status_by_ticket,
    create_complaint_ticket_in_db,
    escalate_complaint_in_db,
    lookup_campus_office
)
from backend.app.services.llm_service import call_llm


def run_complaint_agent(state: CampusAgentState, db: Session) -> Dict[str, Any]:
    """
    Complaint Management Agent:
    - Real ticket status tracking
    - Grievance collection with Human-in-the-Loop confirmation before filing
    - Escalation to Proctorial Board
    """
    query = state["user_query"]
    student_id = state.get("student_id")
    confirmed_action = state.get("confirmed_action")
    action_required = None
    office = lookup_campus_office("complaint") or {
        "office": "Grievance Redressal Cell & Proctorial Board",
        "contact": "Dean Student Welfare Office (Admin Block Room 102)"
    }

    # 1. Check if user has confirmed a pending action
    if confirmed_action and confirmed_action.get("action_type") == "submit_complaint" and student_id:
        details = confirmed_action.get("details", {})
        result = create_complaint_ticket_in_db(
            student_id=student_id,
            category=details.get("category", "General"),
            title=details.get("title", "Student Grievance"),
            description=details.get("description", query),
            priority=details.get("priority", "MEDIUM"),
            db=db
        )
        return {
            "final_response": (
                f"✅ **Complaint Successfully Registered!**\n\n"
                f"- **Ticket ID:** `{result['ticket_id']}`\n"
                f"- **Category:** {details.get('category')}\n"
                f"- **Title:** {details.get('title')}\n"
                f"- **Status:** `PENDING` (Assigned to {office['office']})\n\n"
                f"You can track progress anytime by typing: *'Track complaint {result['ticket_id']}'*."
            ),
            "current_agent": "Complaint Management Agent",
            "source_type": "database",
            "citations": [],
            "action_required": None,
            "office_referral": office,
            "follow_up_suggestions": [
                f"Check status of {result['ticket_id']}",
                "How do I escalate my complaint?",
                "What is the grievance resolution timeline?"
            ]
        }

    # 2. Check for Ticket ID lookup (e.g. CMP-2026-1001)
    ticket_match = re.search(r"\b(CMP-\d{4}-\d{4})\b", query, re.IGNORECASE)
    if ticket_match:
        ticket_id = ticket_match.group(1).upper()

        # Check if student wants to escalate
        if any(w in query.lower() for w in ["escalate", "urgent", "no response", "delay", "take action"]):
            esc_result = escalate_complaint_in_db(ticket_id, "Student requested urgent escalation via CampusAI", db)
            if esc_result["success"]:
                return {
                    "final_response": (
                        f"🚨 **Ticket Escalated Successfully!**\n\n"
                        f"- **Ticket ID:** `{ticket_id}`\n"
                        f"- **New Status:** `ESCALATED` (Priority: CRITICAL)\n"
                        f"- **Escalated To:** Proctorial Board & Dean of Student Welfare\n\n"
                        f"A priority alert has been dispatched to the administration desk for immediate review."
                    ),
                    "current_agent": "Complaint Management Agent",
                    "source_type": "database",
                    "citations": [],
                    "action_required": None,
                    "office_referral": office,
                    "follow_up_suggestions": [f"Status of {ticket_id}", "Contact Dean Office"]
                }

        ticket_info = get_complaint_status_by_ticket(ticket_id, db)
        if ticket_info:
            status_emoji = "🟡" if ticket_info["status"] == "PENDING" else "🔵" if ticket_info["status"] == "IN_REVIEW" else "🟢" if ticket_info["status"] == "RESOLVED" else "🔴"
            resp = (
                f"📋 **Complaint Ticket Record:**\n\n"
                f"- **Ticket ID:** `{ticket_info['ticket_id']}`\n"
                f"- **Title:** {ticket_info['title']}\n"
                f"- **Category:** {ticket_info['category']}\n"
                f"- **Current Status:** {status_emoji} `{ticket_info['status']}`\n"
                f"- **Priority:** `{ticket_info['priority']}`\n"
                f"- **Filed On:** {ticket_info['created_at']}\n"
            )
            if ticket_info.get("escalation_reason"):
                resp += f"\n- **Resolution / Escalation Note:** {ticket_info['escalation_reason']}\n"
            return {
                "final_response": resp,
                "current_agent": "Complaint Management Agent",
                "source_type": "database",
                "citations": [],
                "action_required": None,
                "office_referral": office,
                "follow_up_suggestions": [f"Escalate {ticket_id}", "File a new grievance", "View all my complaints"]
            }
        else:
            return {
                "final_response": f"Ticket ID `{ticket_id}` was not found in the campus grievance registry. Please check the number or view your active complaints in the dashboard.",
                "current_agent": "Complaint Management Agent",
                "source_type": "database",
                "citations": [],
                "action_required": None,
                "office_referral": office,
                "follow_up_suggestions": ["View all my complaints", "File a new complaint"]
            }

    # 3. New complaint filing detection -> Trigger Human-in-the-Loop Approval
    complaint_triggers = [
        "complain", "complaint", "issue", "problem", "broken", "not working", "dirty",
        "down", "disconnected", "leakage", "water problem", "mess food", "grievance",
        "fan not working", "ac not working", "geyser", "repair", "fix", "faulty"
    ]
    if any(t in query.lower() for t in complaint_triggers) and student_id:
        # Determine category and title from query
        cat = "General"
        if any(w in query.lower() for w in ["wifi", "wi-fi", "internet", "lan"]):
            cat = "Wi-Fi"
        elif any(w in query.lower() for w in ["hostel", "room", "washroom", "water", "geyser", "bed"]):
            cat = "Hostel"
        elif any(w in query.lower() for w in ["mess", "food", "dining", "meal", "canteen"]):
            cat = "Hostel Mess"
        elif any(w in query.lower() for w in ["exam", "marks", "grade", "attendance", "lecture", "teacher"]):
            cat = "Academic"
        elif any(w in query.lower() for w in ["fee", "account", "payment", "refund"]):
            cat = "Accounts"

        action_required = {
            "action_type": "submit_complaint",
            "action_title": "Register Formal Complaint Ticket",
            "details": {
                "category": cat,
                "title": query[:120],
                "description": query,
                "priority": "HIGH" if any(w in query.lower() for w in ["urgent", "emergency", "immediately", "critical"]) else "MEDIUM"
            },
            "requires_approval": True
        }

        return {
            "final_response": (
                f"I have prepared a formal grievance ticket for you under category **{cat}**.\n\n"
                f"**Summary:** {query[:120]}\n\n"
                f"⚠️ *Human-in-the-loop confirmation required:* Please review and confirm the action below to record this in the university registry."
            ),
            "current_agent": "Complaint Management Agent",
            "source_type": "action_required",
            "citations": [],
            "action_required": action_required,
            "office_referral": office,
            "follow_up_suggestions": ["Confirm and submit complaint", "Cancel complaint request"]
        }

    # General informational guidance
    prompt = (
        f"Student Query about complaints/grievances: {query}\n"
        "Explain how the student grievance redressal system operates, how to file a ticket, "
        "and direct them to the Grievance Redressal Cell."
    )
    llm_reply = call_llm(prompt, history=state.get("messages", []))

    return {
        "final_response": llm_reply,
        "current_agent": "Complaint Management Agent",
        "source_type": "verified_kb",
        "citations": [],
        "action_required": None,
        "office_referral": office,
        "follow_up_suggestions": [
            "How do I track an existing complaint ticket?",
            "What is the escalation procedure for unresolved issues?",
            "Who is in charge of the Anti-Ragging and Grievance Cell?"
        ]
    }

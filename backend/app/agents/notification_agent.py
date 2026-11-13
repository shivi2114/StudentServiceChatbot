from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.agents.state import CampusAgentState
from backend.app.tools.campus_tools import create_student_reminder_in_db, lookup_campus_office


def run_notification_agent(state: CampusAgentState, db: Session) -> Dict[str, Any]:
    """
    Notification Agent:
    - Sets up exam, fee, and assignment alerts
    - Requires human-in-the-loop confirmation before saving consequential alerts
    """
    query = state["user_query"]
    student_id = state.get("student_id")
    confirmed_action = state.get("confirmed_action")
    office = {
        "office": "Student Welfare Notification Desk",
        "contact": "ERP Alerts & SMS Gateway Cell"
    }

    # 1. Action confirmed by user in UI
    if confirmed_action and confirmed_action.get("action_type") == "create_reminder" and student_id:
        details = confirmed_action.get("details", {})
        res = create_student_reminder_in_db(
            student_id=student_id,
            title=details.get("title", "Campus Reminder"),
            description=details.get("description", query),
            due_date=details.get("due_date", "Upcoming"),
            reminder_type=details.get("reminder_type", "GENERAL"),
            db=db
        )
        return {
            "final_response": (
                f"⏰ **Notification Scheduled Successfully!**\n\n"
                f"- **Title:** {details.get('title')}\n"
                f"- **Target Date:** `{details.get('due_date')}`\n"
                f"- **Alert Type:** `{details.get('reminder_type')}`\n\n"
                f"You will see this active reminder on your Student Dashboard and receive alerts."
            ),
            "current_agent": "Notification Agent",
            "source_type": "database",
            "citations": [],
            "action_required": None,
            "office_referral": office,
            "follow_up_suggestions": ["View all my reminders", "Remind me about fee deadline"]
        }

    # 2. Trigger action approval before creating notification
    rem_type = "GENERAL"
    due_date = "15 Dec 2026"
    title = "Campus Reminder"

    if any(w in query.lower() for w in ["fee", "payment", "due"]):
        rem_type = "FEE"
        title = "Semester Fee Payment Deadline"
        due_date = "15 Dec 2026"
    elif any(w in query.lower() for w in ["exam", "mid-term", "end-term"]):
        rem_type = "EXAM"
        title = "Mid-Term Examination Alert"
        due_date = "25 Nov 2026"
    elif any(w in query.lower() for w in ["scholarship", "form", "income"]):
        rem_type = "GENERAL"
        title = "Scholarship Hard Copy Submission"
        due_date = "30 Nov 2026"

    action_required = {
        "action_type": "create_reminder",
        "action_title": f"Schedule {title}",
        "details": {
            "title": title,
            "description": f"Automated student reminder: {query[:120]}",
            "due_date": due_date,
            "reminder_type": rem_type
        },
        "requires_approval": True
    }

    return {
        "final_response": (
            f"I have prepared an automated notification reminder for you: **{title}**.\n\n"
            f"- **Due Date:** `{due_date}`\n"
            f"- **Type:** `{rem_type}`\n\n"
            f"⚠️ *Human-in-the-loop confirmation required:* Please click confirm below to activate this notification in your student portal."
        ),
        "current_agent": "Notification Agent",
        "source_type": "action_required",
        "citations": [],
        "action_required": action_required,
        "office_referral": office,
        "follow_up_suggestions": ["Confirm and set reminder", "Cancel reminder"]
    }

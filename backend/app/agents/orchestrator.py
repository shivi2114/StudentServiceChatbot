import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from backend.app.agents.state import CampusAgentState
from backend.app.agents.academic_agent import run_academic_agent
from backend.app.agents.fee_agent import run_fee_agent
from backend.app.agents.complaint_agent import run_complaint_agent
from backend.app.agents.scholarship_agent import run_scholarship_agent
from backend.app.agents.placement_agent import run_placement_agent
from backend.app.agents.notification_agent import run_notification_agent
from backend.app.tools.campus_tools import lookup_campus_office
from backend.app.services.llm_service import call_llm


def classify_query_intent(query: str) -> str:
    """Accurately classify user query into the appropriate specialist agent domain."""
    q = query.lower()

    # Direct ticket ID or explicit complaint triggers
    if re.search(r"\b(CMP-\d{4}-\d{4})\b", query, re.IGNORECASE):
        return "complaint"
    if any(w in q for w in ["complaint", "complain", "grievance", "proctor", "ragging", "wifi down", "water problem", "fan not working", "mess food"]):
        return "complaint"

    # Notification / Reminders
    if any(w in q for w in ["remind me", "set reminder", "create alert", "notify me", "set an alarm", "reminder for"]):
        return "notification"

    # Scholarship
    if any(w in q for w in ["scholarship", "fellowship", "pragati", "mcm", "fee waiver", "financial aid", "nsp portal"]):
        return "scholarship"

    # Placement & Career
    if any(w in q for w in ["placement", "internship", "recruitment", "tcs", "cognizant", "ctc", "lpa", "dream company", "mass recruiter", "t&p", "noc"]):
        return "placement"

    # Admission & Fees
    if any(w in q for w in ["fee", "tuition", "hostel fee", "mess fee", "pay online", "payment", "due amount", "refund", "receipt", "erp payment", "owe"]):
        return "fee"

    # Academic & Exams
    if any(w in q for w in ["attendance", "75%", "exam", "mid-term", "end-term", "result", "revaluation", "back-paper", "back paper", "syllabus", "timetable", "marks", "grade", "detained", "condonation"]):
        return "academic"

    # Conversational Greetings & Help
    if any(w in q for w in ["hi", "hello", "hey", "namaste", "good morning", "good afternoon", "thank", "thanks", "who are you", "what can you do"]):
        return "conversational"

    # Default to academic for collegiate queries
    return "academic"


def create_orchestrator_graph(db: Session):
    """Build and compile the LangGraph multi-agent orchestration workflow."""
    workflow = StateGraph(CampusAgentState)

    # 1. Routing Node
    def router_node(state: CampusAgentState) -> Dict[str, Any]:
        user_query = state["user_query"]
        confirmed_action = state.get("confirmed_action")
        
        # If user confirmed an action, route directly to that agent
        if confirmed_action:
            action_type = confirmed_action.get("action_type", "")
            if "complaint" in action_type:
                routed = "complaint"
            elif "reminder" in action_type:
                routed = "notification"
            else:
                routed = classify_query_intent(user_query)
        else:
            routed = classify_query_intent(user_query)

        return {
            "routed_agent": routed,
            "current_agent": "Orchestrator Agent"
        }

    # 2. Specialized Agent Nodes
    def academic_node(state: CampusAgentState) -> Dict[str, Any]:
        return run_academic_agent(state, db)

    def fee_node(state: CampusAgentState) -> Dict[str, Any]:
        return run_fee_agent(state, db)

    def complaint_node(state: CampusAgentState) -> Dict[str, Any]:
        return run_complaint_agent(state, db)

    def scholarship_node(state: CampusAgentState) -> Dict[str, Any]:
        return run_scholarship_agent(state, db)

    def placement_node(state: CampusAgentState) -> Dict[str, Any]:
        return run_placement_agent(state, db)

    def notification_node(state: CampusAgentState) -> Dict[str, Any]:
        return run_notification_agent(state, db)

    def conversational_node(state: CampusAgentState) -> Dict[str, Any]:
        query = state["user_query"]
        language = state.get("language", "en")
        
        if any(w in query.lower() for w in ["hi", "hello", "hey", "namaste", "good morning", "good evening"]):
            ans = (
                "Hello! I am **CampusAI**, your official multi-agent student assistance system. "
                "I collaborate with specialized campus agents to answer academic regulations, check fee ledgers, "
                "register and track complaints, evaluate scholarship eligibility, and guide your placement journey. "
                "How can I assist you today?"
            )
        elif any(w in query.lower() for w in ["thank", "thanks", "thx"]):
            ans = "You're very welcome! Feel free to ask whenever you need guidance with campus services, academics, or facilities."
        else:
            ans = call_llm(
                f"Student says: {query}. Introduce yourself as CampusAI official university assistant and suggest what campus tasks you can handle."
            )

        return {
            "final_response": ans,
            "current_agent": "CampusAI Orchestrator",
            "source_type": "orchestrator",
            "citations": [],
            "action_required": None,
            "office_referral": lookup_campus_office(query) or {
                "office": "College Central Reception",
                "contact": "Main Administration Block"
            },
            "follow_up_suggestions": [
                "What is my current semester attendance?",
                "How much is my pending fee balance?",
                "What are the Tier 1 placement requirements?",
                "How do I file a student complaint?"
            ]
        }

    # Add nodes to graph
    workflow.add_node("router", router_node)
    workflow.add_node("academic", academic_node)
    workflow.add_node("fee", fee_node)
    workflow.add_node("complaint", complaint_node)
    workflow.add_node("scholarship", scholarship_node)
    workflow.add_node("placement", placement_node)
    workflow.add_node("notification", notification_node)
    workflow.add_node("conversational", conversational_node)

    # Entry point
    workflow.set_entry_point("router")

    # Conditional router edges
    def route_decision(state: CampusAgentState) -> str:
        return state.get("routed_agent", "academic")

    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "academic": "academic",
            "fee": "fee",
            "complaint": "complaint",
            "scholarship": "scholarship",
            "placement": "placement",
            "notification": "notification",
            "conversational": "conversational",
        }
    )

    # All agent nodes terminate the turn
    workflow.add_edge("academic", END)
    workflow.add_edge("fee", END)
    workflow.add_edge("complaint", END)
    workflow.add_edge("scholarship", END)
    workflow.add_edge("placement", END)
    workflow.add_edge("notification", END)
    workflow.add_edge("conversational", END)

    return workflow.compile()


def execute_orchestrator(
    query: str,
    user_id: int,
    user_name: str,
    user_role: str,
    student_id: int | None,
    student_profile: Dict[str, Any] | None,
    db: Session,
    history: List[Dict[str, str]] = None,
    language: str = "en",
    confirmed_action: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Execute multi-agent orchestration for a student inquiry."""
    graph = create_orchestrator_graph(db)

    initial_state: CampusAgentState = {
        "messages": history or [],
        "student_id": student_id,
        "user_id": user_id,
        "user_name": user_name,
        "user_role": user_role,
        "student_profile": student_profile,
        "user_query": query,
        "language": language,
        "current_agent": "Orchestrator",
        "routed_agent": "router",
        "intent_category": "",
        "citations": [],
        "tool_results": {},
        "action_required": None,
        "confirmed_action": confirmed_action,
        "final_response": "",
        "source_type": "orchestrator",
        "office_referral": None,
        "follow_up_suggestions": []
    }

    result = graph.invoke(initial_state)
    return result

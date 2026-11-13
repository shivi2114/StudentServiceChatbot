from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator


class CitationItem(TypedDict):
    document_title: str
    source_file: str
    page_number: int
    snippet: str
    relevance_score: Optional[float]


class ActionItem(TypedDict):
    action_type: str
    action_title: str
    details: Dict[str, Any]
    requires_approval: bool


class CampusAgentState(TypedDict):
    # Chat conversation turns
    messages: Annotated[List[Dict[str, str]], operator.add]
    
    # Authenticated user context
    student_id: Optional[int]
    user_id: int
    user_name: str
    user_role: str
    student_profile: Optional[Dict[str, Any]]
    
    # Query parameters
    user_query: str
    language: str  # "en" or "hi"
    
    # Agent orchestration routing
    current_agent: str
    routed_agent: str
    intent_category: str
    
    # Grounding & Citations
    citations: List[CitationItem]
    
    # Tool execution results
    tool_results: Dict[str, Any]
    
    # Human-in-the-loop action approval
    action_required: Optional[ActionItem]
    confirmed_action: Optional[Dict[str, Any]]
    
    # Final combined response
    final_response: str
    source_type: str  # "rag", "database", "verified_kb", "orchestrator", "action_required"
    office_referral: Optional[Dict[str, str]]
    follow_up_suggestions: List[str]

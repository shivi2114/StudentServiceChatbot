import uuid
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import User, StudentProfile, ChatSession, ChatMessage
from backend.app.schemas.all_schemas import (
    ChatQueryRequest, ChatQueryResponse, ChatSessionResponse, ChatMessageSchema
)
from backend.app.services.auth_service import get_current_user
from backend.app.agents.orchestrator import execute_orchestrator

router = APIRouter(prefix="/chat", tags=["Multi-Agent Chat"])


@router.post("", response_model=ChatQueryResponse)
def handle_chat_query(
    payload: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Main Multi-Agent Chat endpoint:
    - Orchestrates specialized agents via LangGraph
    - Executes authorized tools and RAG semantic search
    - Handles human-in-the-loop action confirmations
    - Preserves persistent conversation memory in database
    """
    user_query = payload.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    # 1. Manage or create ChatSession
    session_id = payload.session_id
    session_obj = None
    if session_id:
        session_obj = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        ).first()

    if not session_obj:
        session_id = str(uuid.uuid4())
        session_obj = ChatSession(
            session_id=session_id,
            user_id=current_user.id,
            title=user_query[:50]
        )
        db.add(session_obj)
        db.commit()

    # 2. Retrieve student profile if user is student
    student_id = None
    student_profile_dict = None
    if current_user.role == "student":
        sp = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if sp:
            student_id = sp.id
            student_profile_dict = {
                "roll_number": sp.roll_number,
                "branch": sp.branch,
                "semester": sp.semester,
                "section": sp.section,
                "cgpa": sp.cgpa,
                "hostel_resident": sp.hostel_resident,
                "room_number": sp.room_number
            }

    # 3. Retrieve recent conversation history
    past_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).limit(6).all()

    history_formatted = [{"role": m.role, "content": m.content} for m in past_messages]

    # Save incoming user message
    user_msg_record = ChatMessage(
        session_id=session_id,
        role="user",
        content=user_query
    )
    db.add(user_msg_record)
    db.commit()

    # 4. Execute LangGraph Orchestrator
    try:
        agent_result = execute_orchestrator(
            query=user_query,
            user_id=current_user.id,
            user_name=current_user.full_name,
            user_role=current_user.role,
            student_id=student_id,
            student_profile=student_profile_dict,
            db=db,
            history=history_formatted,
            language=payload.language,
            confirmed_action=payload.confirmed_action
        )
    except Exception as e:
        print(f"[CampusAI Orchestrator Error]: {e}")
        # Safe fallback
        agent_result = {
            "final_response": "I encountered an error coordinating with the campus specialized agents. Please consult the Student Helpdesk or retry your query.",
            "current_agent": "Orchestrator Fallback",
            "source_type": "error",
            "citations": [],
            "action_required": None,
            "office_referral": {"office": "College Central Reception", "contact": "Main Admin Block"},
            "follow_up_suggestions": ["What are the library timings?", "How do I pay fees?"]
        }

    # 5. Persist assistant response to DB
    meta_json = json.dumps({
        "citations": agent_result.get("citations", []),
        "action_required": agent_result.get("action_required"),
        "office_referral": agent_result.get("office_referral")
    })

    assistant_msg_record = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=agent_result.get("final_response", ""),
        agent_name=agent_result.get("current_agent", "Orchestrator"),
        source=agent_result.get("source_type", "orchestrator"),
        metadata_json=meta_json
    )
    db.add(assistant_msg_record)
    db.commit()

    return ChatQueryResponse(
        session_id=session_id,
        answer=agent_result.get("final_response", ""),
        agent_name=agent_result.get("current_agent", "Orchestrator"),
        source=agent_result.get("source_type", "orchestrator"),
        citations=agent_result.get("citations", []),
        action_required=agent_result.get("action_required"),
        office_referral=agent_result.get("office_referral"),
        follow_up_suggestions=agent_result.get("follow_up_suggestions", [])
    )


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_user_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List past chat conversations for the user."""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full message history of a specific chat session."""
    session_obj = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session_obj


@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    session_obj = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Chat session not found")
    db.delete(session_obj)
    db.commit()
    return {"message": "Chat session deleted"}

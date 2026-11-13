import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.entities import (
    User, StudentProfile, Complaint, Announcement, DocumentRecord, ChatMessage
)
from backend.app.schemas.all_schemas import (
    DocumentRecordResponse, ComplaintResponse, AnnouncementResponse
)
from backend.app.services.auth_service import get_current_admin
from backend.app.rag.vector_store import rag_store, DOCUMENTS_DIR

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


@router.get("/analytics")
def get_admin_analytics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retrieve campus analytics, agent performance metrics, and system stats."""
    total_students = db.query(StudentProfile).count()
    total_complaints = db.query(Complaint).count()
    pending_complaints = db.query(Complaint).filter(Complaint.status == "PENDING").count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == "RESOLVED").count()
    escalated_complaints = db.query(Complaint).filter(Complaint.status == "ESCALATED").count()
    total_announcements = db.query(Announcement).count()
    total_queries = db.query(ChatMessage).filter(ChatMessage.role == "user").count()

    # Query agent routing distribution
    assistant_msgs = db.query(ChatMessage).filter(ChatMessage.role == "assistant").all()
    agent_distribution = {}
    for m in assistant_msgs:
        name = m.agent_name or "Orchestrator"
        agent_distribution[name] = agent_distribution.get(name, 0) + 1

    # Documents
    doc_count = len(list(DOCUMENTS_DIR.glob("*.*"))) if DOCUMENTS_DIR.exists() else 0
    chunk_count = len(rag_store.chunks)

    return {
        "total_students": total_students,
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "resolved_complaints": resolved_complaints,
        "escalated_complaints": escalated_complaints,
        "total_announcements": total_announcements,
        "total_queries": total_queries,
        "documents_indexed": doc_count,
        "chunks_indexed": chunk_count,
        "agent_distribution": agent_distribution
    }


@router.get("/documents", response_model=List[Dict[str, Any]])
def list_documents(
    current_admin: User = Depends(get_current_admin)
):
    """List all institutional documents loaded in RAG knowledge base."""
    docs = []
    if DOCUMENTS_DIR.exists():
        for f in DOCUMENTS_DIR.iterdir():
            if f.is_file():
                # count chunks for this file
                chunks_for_file = len([c for c in rag_store.chunks if c.source_file == f.name])
                docs.append({
                    "filename": f.name,
                    "title": f.stem.replace("_", " ").title(),
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "chunk_count": chunks_for_file,
                    "last_modified": f.stat().st_mtime
                })
    return docs


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("General"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin endpoint to upload institutional PDF or text documents for RAG indexing."""
    filename = file.filename
    if not (filename.endswith(".pdf") or filename.endswith(".txt") or filename.endswith(".md")):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf, .txt, and .md files are supported for campus knowledge base."
        )

    dest_path = DOCUMENTS_DIR / filename
    content_bytes = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content_bytes)

    # Re-index RAG vector store
    rag_store.index_documents()
    chunks_created = len([c for c in rag_store.chunks if c.source_file == filename])

    # Record in DB
    doc_rec = DocumentRecord(
        title=title,
        category=category,
        filename=filename,
        file_path=str(dest_path),
        chunk_count=chunks_created,
        uploaded_by=current_admin.email
    )
    db.add(doc_rec)
    db.commit()

    return {
        "success": True,
        "filename": filename,
        "title": title,
        "chunks_indexed": chunks_created,
        "message": f"Document '{title}' successfully embedded and indexed into ChromaDB vector store."
    }


@router.get("/queries")
def get_query_logs(
    limit: int = 50,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retrieve recent student queries, routed agents, and response sources."""
    msgs = db.query(ChatMessage).filter(
        ChatMessage.role == "assistant"
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    logs = []
    for m in msgs:
        logs.append({
            "session_id": m.session_id,
            "agent_name": m.agent_name,
            "source": m.source,
            "timestamp": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
            "content_preview": m.content[:150]
        })
    return logs

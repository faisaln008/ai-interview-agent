import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.agent import run_agent
from app.database import get_db, ConversationLog

router = APIRouter(prefix="/api")

class AskRequest(BaseModel):
    question: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

@router.post("/ask")
async def ask(request: AskRequest, db: Session = Depends(get_db)):
    session_id = request.session_id

    # Fetch the last 5 messages for this session, ordered chronologically.
    recent = (
        db.query(ConversationLog)
        .filter(ConversationLog.session_id == session_id)
        .order_by(ConversationLog.created_at.desc())
        .limit(5)
        .all()
    )
    recent.reverse()  # oldest -> newest
    history = [{"question": r.question, "answer": r.answer} for r in recent]

    result = await run_agent(request.question, history)

    # Persist the new exchange.
    log = ConversationLog(
        session_id=session_id,
        question=request.question,
        answer=result,
    )
    db.add(log)
    db.commit()

    return {"answer": result, "question": request.question, "session_id": session_id}

@router.get("/history/{session_id}")
def history(session_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ConversationLog)
        .filter(ConversationLog.session_id == session_id)
        .order_by(ConversationLog.created_at.desc())
        .limit(10)
        .all()
    )
    rows.reverse()  # oldest -> newest
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": r.id,
                "question": r.question,
                "answer": r.answer,
                "created_at": r.created_at,
            }
            for r in rows
        ],
    }

@router.get("/sessions")
def sessions(db: Session = Depends(get_db)):
    rows = (
        db.query(
            ConversationLog.session_id,
            func.count(ConversationLog.id).label("message_count"),
        )
        .group_by(ConversationLog.session_id)
        .all()
    )
    return {
        "sessions": [
            {"session_id": session_id, "message_count": count}
            for session_id, count in rows
        ]
    }

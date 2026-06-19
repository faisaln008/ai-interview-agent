from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.agent import run_agent

router = APIRouter(prefix="/api")

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask(request: AskRequest):
    result = await run_agent(request.question)
    return {"answer": result, "question": request.question}
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth import get_optional_current_user
from ai.agent import agent

router = APIRouter(tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    tool_called: Optional[str] = None
    tool_output: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
def handle_chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    current_user = get_optional_current_user(token=token, db=db)
    
    # Fallback to requested user_id or default user John (ID: 1) if not logged in
    user_id = current_user.id if current_user else (request.user_id or 1)
    user = db.query(User).filter(User.id == user_id).first()
    user_name = user.name if user else "John"

    response_data = agent.process_message(
        user_message=request.message,
        user_id=user_id,
        user_name=user_name,
        db=db
    )
    return response_data

# server/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    itinerary: Optional[dict] = None
    options: Optional[List[str]] = None
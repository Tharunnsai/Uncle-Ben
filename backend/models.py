from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    id: str
    email: str
    name: str
    google_calendar_token: Optional[str] = None
    created_at: datetime

class ChatMessage(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    conversation_id: str

class Conversation(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

class Appointment(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    google_event_id: Optional[str] = None
    created_at: Optional[datetime] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime

class AppointmentRequest(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

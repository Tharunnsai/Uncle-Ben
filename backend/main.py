from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import uvicorn

from backend.models import (
    LoginRequest, RegisterRequest, ChatRequest, ChatResponse, 
    TokenResponse, AppointmentRequest
)
from backend.auth import create_access_token, get_current_user
from backend.database import db
from backend.chat_service import chat_service
import config

app = FastAPI(title="Chatbot Calendar API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

@app.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    result = await db.create_user(request.email, request.password, request.name)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": result["user"].id,
            "email": result["user"].email
        },
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": result["user"].id,
            "email": result["user"].email,
            "name": request.name
        }
    )

@app.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    result = await db.authenticate_user(request.email, request.password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )
    
    user_data = result["user"]
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user_data["id"],
            "email": user_data["email"]
        },
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_data
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Process chat message"""
    user_id = current_user["id"]
    
    # Create or get conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        # Create new conversation
        conversation = await db.create_conversation(user_id, "New Chat")
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create conversation"
            )
        conversation_id = conversation.id
    
    # Process message with chat service
    response = await chat_service.process_message(user_id, conversation_id, request.message)
    
    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
        timestamp=datetime.utcnow()
    )

@app.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's conversations"""
    conversations = await db.get_user_conversations(current_user["id"])
    return {"conversations": conversations}

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, current_user: dict = Depends(get_current_user)):
    """Get messages for a conversation"""
    messages = await db.get_conversation_messages(conversation_id)
    return {"messages": messages}

@app.get("/appointments")
async def get_appointments(current_user: dict = Depends(get_current_user)):
    """Get user's appointments"""
    appointments = await db.get_user_appointments(current_user["id"])
    return {"appointments": appointments}

@app.post("/google-calendar/connect")
async def connect_google_calendar(current_user: dict = Depends(get_current_user)):
    """Initiate Google Calendar OAuth flow"""
    # This would typically redirect to Google OAuth
    # For now, return instructions
    return {
        "message": "To connect Google Calendar, please provide your Google OAuth credentials",
        "instructions": "This would typically start OAuth flow with Google Calendar API"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
import uvicorn
import json

from backend.models import (
    LoginRequest, RegisterRequest, ChatRequest, ChatResponse, 
    TokenResponse, AppointmentRequest
)
from backend.auth import create_access_token, get_current_user
from backend.database import db
from backend.chat_service import chat_service
import config

# Google Calendar OAuth setup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

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
    """Start Google Calendar OAuth flow"""
    try:
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": config.GOOGLE_CLIENT_ID,
                    "client_secret": config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["https://uncle-ben-backend.onrender.com/google-calendar/callback"]
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = "https://uncle-ben-backend.onrender.com/google-calendar/callback"
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            login_hint=current_user["email"],
            state=current_user["id"]  # Pass user ID in state
        )
        
        return {"auth_url": auth_url, "message": "Click the URL to connect your Google Calendar"}
        
    except Exception as e:
        return {"error": f"OAuth setup error: {str(e)}", "message": "Google Calendar connection failed"}

@app.get("/google-calendar/callback")
async def google_calendar_callback(code: str, state: str = None):
    """Handle Google Calendar OAuth callback"""
    try:
        # Exchange code for credentials
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": config.GOOGLE_CLIENT_ID,
                    "client_secret": config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["https://uncle-ben-backend.onrender.com/google-calendar/callback"]
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        flow.redirect_uri = "https://uncle-ben-backend.onrender.com/google-calendar/callback"
        
        # Fetch token
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save credentials to database (add column if needed)
        if state:  # user_id from state parameter
            try:
                # Add google_calendar_token column if it doesn't exist
                token_data = {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": config.GOOGLE_CLIENT_ID,
                    "client_secret": config.GOOGLE_CLIENT_SECRET,
                    "scopes": list(credentials.scopes) if credentials.scopes else ["https://www.googleapis.com/auth/calendar"]
                }
                
                # Try to update user with Google Calendar token
                db.supabase.table("users").update({
                    "google_calendar_token": json.dumps(token_data)
                }).eq("id", state).execute()
                
                return {"message": "Google Calendar connected successfully! You can now book appointments."}
            except Exception as db_error:
                print(f"Database error: {db_error}")
                return {"message": "Google Calendar connected, but couldn't save to database. Appointments will be saved locally."}
        
        return {"message": "Google Calendar connected successfully"}
        
    except Exception as e:
        return {"error": f"OAuth callback error: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

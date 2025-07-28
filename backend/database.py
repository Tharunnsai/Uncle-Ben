import os
from supabase import create_client, Client
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from backend.models import User, ChatMessage, Conversation, Appointment
import config

class Database:
    def __init__(self):
        self.supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    async def create_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Create a new user with Supabase Auth"""
        try:
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if auth_response.user:
                # Insert user data into our users table
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "name": name,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table("users").insert(user_data).execute()
                return {"success": True, "user": auth_response.user}
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Supabase Auth"""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Get user data from our users table
                user_result = self.supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
                
                if user_result.data:
                    return {
                        "success": True, 
                        "user": user_result.data[0],
                        "session": auth_response.session
                    }
                else:
                    return {"success": False, "error": "User data not found"}
            else:
                return {"success": False, "error": "Invalid credentials"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            result = self.supabase.table("conversations").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            return [Conversation(**conv) for conv in result.data]
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    async def create_conversation(self, user_id: str, title: str) -> Optional[Conversation]:
        """Create a new conversation"""
        try:
            conversation_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("conversations").insert(conversation_data).execute()
            if result.data:
                return Conversation(**result.data[0])
            return None
        except Exception as e:
            print(f"Error creating conversation: {e}")
            return None
    
    async def get_conversation_messages(self, conversation_id: str) -> List[ChatMessage]:
        """Get all messages for a conversation"""
        try:
            result = self.supabase.table("chat_messages").select("*").eq("conversation_id", conversation_id).order("timestamp", desc=False).execute()
            return [ChatMessage(**msg) for msg in result.data]
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    async def save_message(self, user_id: str, conversation_id: str, content: str, role: str) -> Optional[ChatMessage]:
        """Save a chat message"""
        try:
            message_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "conversation_id": conversation_id,
                "content": content,
                "role": role,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("chat_messages").insert(message_data).execute()
            
            # Update conversation timestamp
            self.supabase.table("conversations").update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", conversation_id).execute()
            
            if result.data:
                return ChatMessage(**result.data[0])
            return None
        except Exception as e:
            print(f"Error saving message: {e}")
            return None
    
    async def save_appointment(self, appointment: Appointment) -> Optional[Appointment]:
        """Save an appointment"""
        try:
            appointment_data = {
                "id": str(uuid.uuid4()),
                "user_id": appointment.user_id,
                "title": appointment.title,
                "description": appointment.description,
                "start_time": appointment.start_time.isoformat(),
                "end_time": appointment.end_time.isoformat(),
                "google_event_id": appointment.google_event_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("appointments").insert(appointment_data).execute()
            if result.data:
                return Appointment(**result.data[0])
            return None
        except Exception as e:
            print(f"Error saving appointment: {e}")
            return None
    
    async def get_user_appointments(self, user_id: str) -> List[Appointment]:
        """Get all appointments for a user"""
        try:
            result = self.supabase.table("appointments").select("*").eq("user_id", user_id).order("start_time", desc=False).execute()
            return [Appointment(**apt) for apt in result.data]
        except Exception as e:
            print(f"Error getting appointments: {e}")
            return []
    
    async def update_user_google_token(self, user_id: str, token: str) -> bool:
        """Update user's Google Calendar token"""
        try:
            result = self.supabase.table("users").update({
                "google_calendar_token": token
            }).eq("id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating Google token: {e}")
            return False

# Global database instance
db = Database()

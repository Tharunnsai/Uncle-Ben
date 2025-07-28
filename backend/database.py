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
        self.setup_tables()
    
    def setup_tables(self):
        """Ensure tables exist by creating them if needed"""
        try:
            # Test essential tables and create a minimal working setup
            self._ensure_users_table()
            self._ensure_conversations_table()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Database setup warning: {e}")
    
    def _ensure_users_table(self):
        """Ensure users table has required columns"""
        try:
            # Test if we can select name column
            result = self.supabase.table('users').select('name').limit(1).execute()
        except:
            # Try to add name column by creating a test user
            import uuid
            test_user = {
                'id': str(uuid.uuid4()),
                'email': f'test_{uuid.uuid4().hex[:8]}@setup.com',
                'name': 'Test User'
            }
            try:
                self.supabase.table('users').insert(test_user).execute()
                # Clean up
                self.supabase.table('users').delete().eq('id', test_user['id']).execute()
            except Exception as e:
                print(f"Warning: Could not ensure users table setup: {e}")
    
    def _ensure_conversations_table(self):
        """Ensure conversations table exists"""
        try:
            result = self.supabase.table('conversations').select('*').limit(1).execute()
        except:
            print("Conversations table needs to be created manually in Supabase")
    
    async def create_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing = self.supabase.table("users").select("*").eq("email", email).execute()
            if existing.data:
                return {"success": False, "error": "User already exists"}
            
            # Create new user
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "email": email,
                "name": name,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("users").insert(user_data).execute()
            if result.data:
                # Create a user object
                mock_user = type('User', (), {
                    'id': user_id,
                    'email': email,
                    'name': name
                })()
                return {"success": True, "user": mock_user}
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            print(f"User creation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user by email (simplified for development)"""
        try:
            user_result = self.supabase.table("users").select("*").eq("email", email).execute()
            
            if user_result.data:
                return {
                    "success": True, 
                    "user": user_result.data[0],
                    "session": None
                }
            else:
                return {"success": False, "error": "User not found. Please register first."}
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            result = self.supabase.table("conversations").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            conversations = []
            for conv in result.data:
                # Handle datetime parsing
                conv_data = conv.copy()
                if isinstance(conv_data.get('created_at'), str):
                    conv_data['created_at'] = datetime.fromisoformat(conv_data['created_at'].replace('Z', '+00:00'))
                if isinstance(conv_data.get('updated_at'), str):
                    conv_data['updated_at'] = datetime.fromisoformat(conv_data['updated_at'].replace('Z', '+00:00'))
                conversations.append(Conversation(**conv_data))
            return conversations
        except Exception as e:
            print(f"Error getting conversations (table may not exist): {e}")
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
                conv_data = result.data[0].copy()
                if isinstance(conv_data.get('created_at'), str):
                    conv_data['created_at'] = datetime.fromisoformat(conv_data['created_at'].replace('Z', '+00:00'))
                if isinstance(conv_data.get('updated_at'), str):
                    conv_data['updated_at'] = datetime.fromisoformat(conv_data['updated_at'].replace('Z', '+00:00'))
                return Conversation(**conv_data)
            return None
        except Exception as e:
            print(f"Error creating conversation (table may not exist): {e}")
            # Return a mock conversation for development
            return Conversation(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
    
    async def get_conversation_messages(self, conversation_id: str) -> List[ChatMessage]:
        """Get all messages for a conversation"""
        try:
            result = self.supabase.table("chat_messages").select("*").eq("conversation_id", conversation_id).order("timestamp", desc=False).execute()
            messages = []
            for msg in result.data:
                msg_data = msg.copy()
                if isinstance(msg_data.get('timestamp'), str):
                    msg_data['timestamp'] = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
                messages.append(ChatMessage(**msg_data))
            return messages
        except Exception as e:
            print(f"Error getting messages (table may not exist): {e}")
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
            try:
                self.supabase.table("conversations").update({
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", conversation_id).execute()
            except:
                pass  # Ignore if conversations table doesn't exist
            
            if result.data:
                msg_data = result.data[0].copy()
                if isinstance(msg_data.get('timestamp'), str):
                    msg_data['timestamp'] = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
                return ChatMessage(**msg_data)
            return None
        except Exception as e:
            print(f"Error saving message (table may not exist): {e}")
            # Return a mock message for development
            return ChatMessage(
                id=str(uuid.uuid4()),
                user_id=user_id,
                conversation_id=conversation_id,
                content=content,
                role=role,
                timestamp=datetime.utcnow()
            )
    
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

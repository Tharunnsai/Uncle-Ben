from langchain.tools import tool
from typing import Dict, Any, List
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from backend.database import db
from backend.models import Appointment
import json

class GoogleCalendarTools:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.service = None
    
    async def _get_calendar_service(self):
        """Initialize Google Calendar service with user's token"""
        try:
            # Get user's Google token from database
            user_result = db.supabase.table("users").select("google_calendar_token").eq("id", self.user_id).execute()
            
            if not user_result.data or not user_result.data[0].get("google_calendar_token"):
                return None
            
            token_data = json.loads(user_result.data[0]["google_calendar_token"])
            credentials = Credentials.from_authorized_user_info(token_data)
            
            self.service = build('calendar', 'v3', credentials=credentials)
            return self.service
        except Exception as e:
            print(f"Error initializing calendar service: {e}")
            return None

@tool
def book_appointment(title: str, description: str, start_time: str, end_time: str, user_id: str) -> str:
    """
    Book a new appointment in Google Calendar.
    
    Args:
        title: The title of the appointment
        description: Description of the appointment
        start_time: Start time in ISO format (e.g., '2024-01-15T10:00:00')
        end_time: End time in ISO format (e.g., '2024-01-15T11:00:00')
        user_id: The user's ID
    
    Returns:
        Success or error message
    """
    try:
        import asyncio
        calendar_tools = GoogleCalendarTools(user_id)
        service = asyncio.run(calendar_tools._get_calendar_service())
        
        if not service:
            return "Error: Google Calendar not connected. Please connect your Google Calendar first."
        
        # Create event
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }
        
        # Insert event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        # Save to database
        appointment = Appointment(
            user_id=user_id,
            title=title,
            description=description,
            start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(end_time.replace('Z', '+00:00')),
            google_event_id=created_event['id']
        )
        
        saved_appointment = asyncio.run(db.save_appointment(appointment))
        
        if saved_appointment:
            return f"✅ Appointment '{title}' booked successfully for {start_time} to {end_time}"
        else:
            return "❌ Error saving appointment to database"
            
    except Exception as e:
        return f"❌ Error booking appointment: {str(e)}"

@tool
def get_appointments(user_id: str, date: str = "") -> str:
    """
    Get user's appointments from Google Calendar.
    
    Args:
        user_id: The user's ID
        date: Optional date filter in YYYY-MM-DD format
    
    Returns:
        List of appointments
    """
    try:
        import asyncio
        calendar_tools = GoogleCalendarTools(user_id)
        service = asyncio.run(calendar_tools._get_calendar_service())
        
        if not service:
            return "Error: Google Calendar not connected. Please connect your Google Calendar first."
        
        # Set time bounds
        if date:
            time_min = f"{date}T00:00:00Z"
            time_max = f"{date}T23:59:59Z"
        else:
            time_min = datetime.utcnow().isoformat() + 'Z'
            time_max = None
        
        # Get events
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "📅 No appointments found."
        
        appointments_text = "📅 Your appointments:\n\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            title = event.get('summary', 'No title')
            description = event.get('description', '')
            
            appointments_text += f"• **{title}**\n"
            appointments_text += f"  Time: {start} to {end}\n"
            if description:
                appointments_text += f"  Description: {description}\n"
            appointments_text += "\n"
        
        return appointments_text
        
    except Exception as e:
        return f"❌ Error retrieving appointments: {str(e)}"

@tool
def cancel_appointment(event_id: str, user_id: str) -> str:
    """
    Cancel an appointment in Google Calendar.
    
    Args:
        event_id: The Google Calendar event ID
        user_id: The user's ID
    
    Returns:
        Success or error message
    """
    try:
        import asyncio
        calendar_tools = GoogleCalendarTools(user_id)
        service = asyncio.run(calendar_tools._get_calendar_service())
        
        if not service:
            return "Error: Google Calendar not connected. Please connect your Google Calendar first."
        
        # Delete event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        
        return f"✅ Appointment cancelled successfully"
        
    except Exception as e:
        return f"❌ Error cancelling appointment: {str(e)}"

@tool
def check_availability(user_id: str, start_time: str, end_time: str) -> str:
    """
    Check availability for a time slot.
    
    Args:
        user_id: The user's ID
        start_time: Start time in ISO format
        end_time: End time in ISO format
    
    Returns:
        Availability status
    """
    try:
        import asyncio
        calendar_tools = GoogleCalendarTools(user_id)
        service = asyncio.run(calendar_tools._get_calendar_service())
        
        if not service:
            return "Error: Google Calendar not connected. Please connect your Google Calendar first."
        
        # Check for conflicts
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True
        ).execute()
        
        events = events_result.get('items', [])
        
        if events:
            conflicts = []
            for event in events:
                title = event.get('summary', 'No title')
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                conflicts.append(f"• {title} ({event_start} to {event_end})")
            
            return f"❌ Time slot not available. Conflicts found:\n" + "\n".join(conflicts)
        else:
            return f"✅ Time slot available from {start_time} to {end_time}"
            
    except Exception as e:
        return f"❌ Error checking availability: {str(e)}"

# Tool list for LangGraph
calendar_tools = [book_appointment, get_appointments, cancel_appointment, check_availability]

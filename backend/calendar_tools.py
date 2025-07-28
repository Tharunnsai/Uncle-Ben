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
            # Check if user has Google Calendar token
            user_result = db.supabase.table("users").select("*").eq("id", self.user_id).execute()
            
            if not user_result.data:
                return None
                
            # Check if user has Google Calendar token in database
            user_data = user_result.data[0]
            if not user_data.get("google_calendar_token"):
                return None
            
            # Parse and use the stored credentials
            token_data = json.loads(user_data["google_calendar_token"])
            credentials = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get("token_uri"),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes")
            )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            return self.service
        except Exception as e:
            print(f"Error initializing calendar service: {e}")
            return None

@tool
def book_appointment(user_id: str, title: str, start_time: str, end_time: str, description: str = "") -> str:
    """
    Book a new appointment in Google Calendar.
    
    Args:
        user_id: The user's ID
        title: The title of the appointment
        start_time: Start time in ISO format (e.g., '2024-01-15T10:00:00')
        end_time: End time in ISO format (e.g., '2024-01-15T11:00:00') 
        description: Description of the appointment
    
    Returns:
        Success or error message
    """
    try:
        # Try Google Calendar first
        try:
            calendar_tools = GoogleCalendarTools(user_id)
            
            # Check if running in async context
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                # We're in an async context, create new loop
                import threading
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        service = new_loop.run_until_complete(calendar_tools._get_calendar_service())
                        return service
                    finally:
                        new_loop.close()
                
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    service = future.result(timeout=10)
                    
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                import asyncio
                service = asyncio.run(calendar_tools._get_calendar_service())
            
            if service:
                # Create Google Calendar event
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
                
                created_event = service.events().insert(calendarId='primary', body=event).execute()
                google_event_id = created_event['id']
            else:
                google_event_id = None
                
        except Exception as google_error:
            print(f"Google Calendar error: {google_error}")
            google_event_id = None
        
        # Always save to local database
        appointment = Appointment(
            user_id=user_id,
            title=title,
            description=description,
            start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(end_time.replace('Z', '+00:00')),
            google_event_id=google_event_id
        )
        
        # Run database save in proper async context
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            # Create task in current loop
            task = loop.create_task(db.save_appointment(appointment))
            # Wait for completion using gather
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, db.save_appointment(appointment))
                saved_appointment = future.result(timeout=10)
        except RuntimeError:
            # No event loop, safe to use asyncio.run
            import asyncio
            saved_appointment = asyncio.run(db.save_appointment(appointment))
        except:
            saved_appointment = None
        
        # Format the datetime for display
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        formatted_time = start_dt.strftime('%B %d, %Y at %I:%M %p')
        
        if google_event_id:
            return f"✅ Appointment '{title}' booked successfully for {formatted_time} and synced with Google Calendar"
        else:
            return f"✅ Appointment '{title}' booked successfully for {formatted_time} (saved locally - Google Calendar connection pending)"
            
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
        # Get appointments from local database first
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                # Use thread executor for database call
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, db.get_user_appointments(user_id))
                    local_appointments = future.result(timeout=10)
            except RuntimeError:
                local_appointments = asyncio.run(db.get_user_appointments(user_id))
        except:
            local_appointments = []
        
        # Try to get from Google Calendar as well
        google_events = []
        try:
            calendar_tools = GoogleCalendarTools(user_id)
            
            # Handle async context properly
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, calendar_tools._get_calendar_service())
                    service = future.result(timeout=10)
            except RuntimeError:
                import asyncio
                service = asyncio.run(calendar_tools._get_calendar_service())
            
            if service:
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
                
                google_events = events_result.get('items', [])
        except Exception as google_error:
            print(f"Google Calendar fetch error: {google_error}")
        
        # Combine and format results
        appointments_text = "📅 Your appointments:\n\n"
        
        # Add local appointments
        if local_appointments:
            for apt in local_appointments:
                appointments_text += f"• **{apt.title}**\n"
                appointments_text += f"  Time: {apt.start_time.strftime('%Y-%m-%d %H:%M')} to {apt.end_time.strftime('%Y-%m-%d %H:%M')}\n"
                if apt.description:
                    appointments_text += f"  Description: {apt.description}\n"
                sync_status = "✅ Synced" if apt.google_event_id else "📱 Local"
                appointments_text += f"  Status: {sync_status}\n\n"
        
        # Add Google-only events (not in local db)
        local_google_ids = {apt.google_event_id for apt in local_appointments if apt.google_event_id}
        for event in google_events:
            if event.get('id') not in local_google_ids:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                title = event.get('summary', 'No title')
                description = event.get('description', '')
                
                appointments_text += f"• **{title}** (Google only)\n"
                appointments_text += f"  Time: {start} to {end}\n"
                if description:
                    appointments_text += f"  Description: {description}\n"
                appointments_text += "\n"
        
        if not local_appointments and not google_events:
            return "📅 No appointments found."
        
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

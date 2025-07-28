import streamlit as st
import requests
import json
from datetime import datetime
import config

# Page configuration
st.set_page_config(
    page_title="AI Calendar Assistant",
    page_icon="🤖",
    layout="wide"
)

# Backend API base URL
API_BASE = config.BACKEND_URL

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def make_api_request(endpoint, method="GET", data=None, auth_required=True):
    """Make API request to backend"""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if auth_required and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        response = None
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response and response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response:
            return {"success": False, "error": response.text}
        else:
            return {"success": False, "error": "No response received"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_page():
    """Login/Register page"""
    st.title("🤖 AI Calendar Assistant")
    st.markdown("Your intelligent appointment management companion")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login and email and password:
                with st.spinner("Logging in..."):
                    result = make_api_request(
                        "/login",
                        method="POST",
                        data={"email": email, "password": password},
                        auth_required=False
                    )
                    
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user = result["data"]["user"]
                        st.session_state.token = result["data"]["access_token"]
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_register = st.form_submit_button("Register")
            
            if submit_register and name and email and password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    with st.spinner("Creating account..."):
                        result = make_api_request(
                            "/register",
                            method="POST",
                            data={"email": email, "password": password, "name": name},
                            auth_required=False
                        )
                        
                        if result["success"]:
                            st.session_state.authenticated = True
                            st.session_state.user = result["data"]["user"]
                            st.session_state.token = result["data"]["access_token"]
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.error(f"Registration failed: {result['error']}")

def load_conversation_history():
    """Load conversation history from backend"""
    result = make_api_request("/conversations")
    if result["success"]:
        return result["data"]["conversations"]
    return []

def load_messages(conversation_id):
    """Load messages for a conversation"""
    result = make_api_request(f"/conversations/{conversation_id}/messages")
    if result["success"]:
        return result["data"]["messages"]
    return []

def send_message(message, conversation_id=None):
    """Send message to backend"""
    data = {"message": message}
    if conversation_id:
        data["conversation_id"] = conversation_id
    
    result = make_api_request("/chat", method="POST", data=data)
    return result

def main_chat_interface():
    """Main chat interface"""
    st.title("🤖 AI Calendar Assistant")
    
    # Sidebar with user info and conversations
    with st.sidebar:
        st.markdown(f"**Welcome, {st.session_state.user['name']}!**")
        
        if st.button("🔓 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # New conversation button
        if st.button("💬 New Conversation"):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        # Conversation history
        st.subheader("📋 Recent Conversations")
        conversations = load_conversation_history()
        
        for conv in conversations[:10]:  # Show last 10 conversations
            if st.button(f"📝 {conv['title'][:20]}...", key=f"conv_{conv['id']}"):
                st.session_state.current_conversation_id = conv['id']
                st.session_state.messages = load_messages(conv['id'])
                st.rerun()
        
        st.markdown("---")
        
        # Google Calendar connection
        st.subheader("📅 Google Calendar")
        if st.button("🔗 Connect Calendar"):
            result = make_api_request("/google-calendar/connect", method="POST")
            if result["success"]:
                st.success("Calendar connection initiated!")
            else:
                st.error("Failed to connect calendar")
        
        # Quick appointment view
        st.subheader("📋 Upcoming Appointments")
        appointments_result = make_api_request("/appointments")
        if appointments_result["success"]:
            appointments = appointments_result["data"]["appointments"]
            if appointments:
                for apt in appointments[:3]:  # Show next 3 appointments
                    st.markdown(f"**{apt['title']}**")
                    st.markdown(f"🕐 {apt['start_time']}")
            else:
                st.markdown("*No upcoming appointments*")
    
    # Main chat area
    st.markdown("### 💬 Chat with your AI Assistant")
    st.markdown("I can help you manage your calendar appointments, book meetings, and check your schedule!")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.messages:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])
        else:
            # Welcome message
            with st.chat_message("assistant"):
                st.write("👋 Hello! I'm your AI Calendar Assistant. I can help you:")
                st.write("• 📅 Book new appointments")
                st.write("• 📋 View your schedule")
                st.write("• ❌ Cancel appointments")
                st.write("• 🔄 Reschedule meetings")
                st.write("• ✅ Check availability")
                st.write("\nJust tell me what you'd like to do!")
    
    # Chat input
    with st.container():
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to display immediately
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Send to backend and get response
            with st.spinner("Thinking..."):
                result = send_message(prompt, st.session_state.current_conversation_id)
                
                if result["success"]:
                    response_data = result["data"]
                    response_text = response_data["response"]
                    
                    # Update conversation ID if new
                    if not st.session_state.current_conversation_id:
                        st.session_state.current_conversation_id = response_data["conversation_id"]
                    
                    # Add assistant response
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.write(response_text)
                else:
                    error_msg = f"Sorry, I encountered an error: {result['error']}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
                    with st.chat_message("assistant"):
                        st.error(error_msg)
            
            st.rerun()

# Main app logic
def main():
    """Main application"""
    # Check backend health
    health_result = make_api_request("/health", auth_required=False)
    if not health_result["success"]:
        st.error("⚠️ Backend service is not available. Please ensure the backend is running.")
        st.code("To start the backend, run: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        return
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_chat_interface()

if __name__ == "__main__":
    main()

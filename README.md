# 🤖 Uncle Ben - AI Calendar Assistant

> *"With great power comes great responsibility... and great scheduling!"*

Uncle Ben is an intelligent AI-powered calendar assistant that helps you manage appointments, schedule meetings, and organize your time efficiently. Built with modern web technologies and powered by Groq's AI models, Uncle Ben provides a conversational interface for all your calendar management needs.

## ✨ Features

### 🗣️ **Conversational AI Interface**
- Natural language chat with Uncle Ben
- Book appointments using plain English
- Reschedule and cancel meetings effortlessly
- Check availability and view your schedule
- AI-powered suggestions for optimal scheduling

### 📅 **Calendar Integration**
- **Google Calendar** integration for seamless sync
- Real-time appointment management
- Automatic event creation and updates
- Cross-platform calendar access

### 🔐 **Secure Authentication**
- User registration and login system
- JWT-based authentication
- Supabase-powered user management
- Secure data storage and retrieval

### 💬 **Conversation History**
- Persistent chat conversations
- Context-aware AI responses
- Conversation management and organization
- Search through past interactions

### 🎯 **Smart Features**
- AI-powered appointment suggestions
- Conflict detection and resolution
- Time zone handling
- Recurring appointment support

## 🏗️ Architecture

### **Frontend**
- **Streamlit** - Modern web interface
- **React-like components** for interactive UI
- **Real-time chat** interface
- **Responsive design** for all devices

### **Backend**
- **FastAPI** - High-performance API
- **Supabase** - PostgreSQL database with real-time features
- **Groq AI** - Advanced language model integration
- **Google Calendar API** - Calendar synchronization

### **AI Integration**
- **Groq's Llama3-70B** model for natural language processing
- **LangChain** for AI workflow orchestration
- **Custom tools** for calendar operations
- **Context-aware** responses

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account
- Google Cloud Platform account (for Calendar API)
- Groq API key

### 1. **Clone the Repository**
```bash
git clone https://github.com/your-username/uncle-ben.git
cd uncle-ben
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Environment Setup**
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_service_role_key_here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Groq AI API
GROQ_API_KEY=your_groq_api_key_here

# JWT Secret (generate a random string)
JWT_SECRET=your_jwt_secret_here
```

### 4. **Database Setup**
Follow the database setup instructions in `README_DATABASE_SETUP.md` or run the SQL commands in your Supabase dashboard.

### 5. **Start the Application**

**Start the Backend:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Start the Frontend (in a new terminal):**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 6. **Access Uncle Ben**
Open your browser and navigate to: **http://localhost:8501**

## 🌐 Deployment

### **Backend Deployment (Render)**

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service** using the `render.yaml` file
3. **Set Environment Variables** in Render dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GROQ_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `JWT_SECRET`
4. **Deploy** - Render will automatically build and deploy your backend

### **Frontend Deployment (Streamlit Cloud)**

1. **Connect your GitHub repository to Streamlit Cloud**
2. **Set Environment Variables** in Streamlit Cloud:
   - `BACKEND_URL` = Your Render backend URL (e.g., `https://uncle-ben-backend.onrender.com`)
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GROQ_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `JWT_SECRET`
3. **Deploy** - Streamlit Cloud will deploy your frontend

### **Deployment URLs**
- **Backend**: `https://your-backend-name.onrender.com`
- **Frontend**: `https://your-app-name.streamlit.app`

## 🎯 Usage Examples

### **Booking Appointments**
```
User: "I need to schedule a meeting with John tomorrow at 2 PM"
Uncle Ben: "I'll schedule a meeting with John for tomorrow at 2:00 PM. The meeting will be 1 hour by default. Would you like me to adjust the duration or add any specific details?"
```

### **Checking Schedule**
```
User: "What's on my calendar for this week?"
Uncle Ben: "Here's your schedule for this week:
- Monday: Team standup (9:00 AM - 9:30 AM)
- Tuesday: Client meeting with ABC Corp (2:00 PM - 3:00 PM)
- Wednesday: Free
- Thursday: Project review (10:00 AM - 11:00 AM)
- Friday: Lunch with Sarah (12:00 PM - 1:00 PM)"
```

### **Rescheduling**
```
User: "Can you move my 2 PM meeting to 3 PM?"
Uncle Ben: "I've rescheduled your 2:00 PM meeting with John to 3:00 PM. The meeting duration remains 1 hour. You'll receive a calendar update notification."
```

## 🔧 Configuration

### **Supabase Setup**
1. Create a new Supabase project
2. Get your project URL and service role key
3. Run the database setup SQL commands
4. Update your `.env` file with the credentials

### **Google Calendar Integration**
1. Create a Google Cloud Platform project
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Add the credentials to your `.env` file

### **Groq AI Setup**
1. Sign up for a Groq account
2. Generate an API key
3. Add the key to your `.env` file

## 📁 Project Structure

```
ChatMind/
├── app.py                 # Streamlit frontend
├── config.py             # Configuration and environment variables
├── backend/
│   ├── main.py           # FastAPI application
│   ├── auth.py           # Authentication logic
│   ├── database.py       # Database operations
│   ├── chat_service.py   # AI chat service
│   ├── calendar_tools.py # Calendar integration tools
│   └── models.py         # Pydantic models
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## 🛠️ Development

### **Running in Development Mode**
```bash
# Backend with auto-reload
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend with auto-reload
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### **Testing**
```bash
# Run backend tests
python -m pytest tests/backend/

# Run frontend tests
python -m pytest tests/frontend/
```

## 🔒 Security

- **Environment Variables**: All sensitive data is stored in environment variables
- **JWT Authentication**: Secure token-based authentication
- **Supabase RLS**: Row-level security for data isolation
- **HTTPS**: All API communications are encrypted
- **Input Validation**: Comprehensive input sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing the AI models
- **Supabase** for the database infrastructure
- **Streamlit** for the web framework
- **FastAPI** for the backend framework
- **Google Calendar API** for calendar integration

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/uncle-ben/issues) page
2. Create a new issue with detailed information
3. Join our [Discord community](https://discord.gg/uncle-ben)

---

**"With Uncle Ben, every day is a well-organized adventure!"** 🕷️✨ 
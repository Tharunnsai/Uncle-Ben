# AI Calendar Assistant

## Overview

This is an AI-powered calendar assistant application that combines a Streamlit frontend with a FastAPI backend. The system allows users to interact with an AI chatbot that can manage their Google Calendar events through natural language conversations. The application uses LangGraph for conversation flow management and integrates with Google Calendar API for calendar operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a client-server architecture with the following components:

### Frontend Architecture
- **Framework**: Streamlit web application
- **Purpose**: Provides a conversational interface for users to interact with the AI assistant
- **Authentication**: Session-based authentication with JWT tokens
- **Communication**: RESTful API calls to the backend

### Backend Architecture
- **Framework**: FastAPI with Python
- **Architecture Pattern**: Microservices-style with modular components
- **AI Integration**: LangGraph for conversation management with Groq LLM
- **Authentication**: JWT-based authentication with Supabase Auth

## Key Components

### 1. Authentication System
- **Technology**: Supabase Auth with JWT tokens
- **Implementation**: Custom JWT handling in `backend/auth.py`
- **Security**: Bearer token authentication for API endpoints
- **Rationale**: Supabase provides robust authentication infrastructure while maintaining control over user data

### 2. Chat Service
- **Technology**: LangGraph with ChatGroq LLM (DeepSeek model)
- **Purpose**: Manages conversational AI flow and tool execution
- **Features**: State management for conversations, tool binding for calendar operations
- **Rationale**: LangGraph provides structured conversation flow management with tool integration capabilities

### 3. Calendar Integration
- **Technology**: Google Calendar API with OAuth2
- **Implementation**: Calendar tools in `backend/calendar_tools.py`
- **Functionality**: Create, read, update appointments through natural language
- **Authentication**: OAuth2 tokens stored in user profiles

### 4. Database Layer
- **Technology**: Supabase (PostgreSQL-based)
- **Purpose**: User management, conversation history, appointment metadata
- **Models**: Users, ChatMessages, Conversations, Appointments
- **Rationale**: Supabase provides managed PostgreSQL with built-in authentication

## Data Flow

1. **User Authentication**: Users register/login through Streamlit frontend
2. **JWT Token Management**: Backend issues JWT tokens for authenticated sessions
3. **Chat Interaction**: Users send messages through Streamlit to FastAPI backend
4. **AI Processing**: LangGraph processes messages and determines required actions
5. **Tool Execution**: Calendar tools execute Google Calendar operations when needed
6. **Response Generation**: AI generates human-readable responses about calendar actions
7. **Data Persistence**: Conversations and appointments stored in Supabase

## External Dependencies

### Required Services
- **Groq API**: LLM inference service for conversation AI
- **Supabase**: Database and authentication service
- **Google Calendar API**: Calendar operations and OAuth2 authentication

### API Keys Required
- `GROQ_API_KEY`: For AI model access
- `SUPABASE_URL` and `SUPABASE_KEY`: For database operations
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: For Google Calendar integration
- `JWT_SECRET`: For token signing

### Python Dependencies
- FastAPI for backend API
- Streamlit for frontend
- LangChain and LangGraph for AI workflow
- Supabase Python client
- Google Calendar API client
- PyJWT for token management

## Deployment Strategy

### Development Environment
- Backend runs on `localhost:8000` (FastAPI with uvicorn)
- Frontend runs on Streamlit's default port
- Environment variables loaded from system environment

### Production Considerations
- Backend URL configurable via `BACKEND_URL` environment variable
- All sensitive configuration via environment variables
- CORS enabled for cross-origin requests
- JWT tokens with configurable expiration (default 24 hours)

### Architecture Benefits
- **Modularity**: Clear separation between frontend, backend, and external services
- **Scalability**: Stateless backend with external database
- **Security**: JWT-based authentication with OAuth2 for Google services
- **Maintainability**: Structured code with clear separation of concerns
- **Extensibility**: LangGraph allows easy addition of new tools and conversation flows

## Recent Changes (July 28, 2025)
- ✓ Built complete AI Calendar Assistant application
- ✓ Integrated Streamlit frontend with FastAPI backend
- ✓ Implemented Groq DeepSeek LLM with LangGraph conversation flow
- ✓ Added Google Calendar API tools for appointment management
- ✓ Set up Supabase database integration with JWT authentication
- → Database tables need to be created in Supabase dashboard (see QUICK_START.md)

## Current Status
- Backend API running on port 8000
- Streamlit frontend running on port 5000
- All API keys and secrets configured
- Database connection established
- Waiting for user to create database tables

### Potential Improvements
- Add rate limiting for API endpoints
- Implement caching for frequently accessed data
- Add error handling and retry mechanisms for external API calls
- Consider adding real-time features with WebSockets
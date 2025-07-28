# Quick Start Guide - AI Calendar Assistant

## 🚨 Database Setup Required

Your application is ready but needs database tables. Here's exactly what to do:

### Step 1: Open Supabase Dashboard
1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Open your project
3. Click "SQL Editor" in the left sidebar

### Step 2: Run This SQL Command
Copy and paste this EXACT command in the SQL Editor and click "RUN":

```sql
-- Add name column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255);

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create appointments table
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    google_event_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Step 3: Test the Application
After running the SQL:
1. Refresh your application page
2. Try registering a new account
3. Start chatting with the AI assistant

## 🎉 Your AI Calendar Assistant Features:
- User registration and login
- AI-powered chat interface using Groq's DeepSeek model
- Google Calendar integration for appointments
- Conversation history
- Appointment management (book, view, cancel, reschedule)

## Troubleshooting:
- If you see "Not Found" errors, the database tables haven't been created yet
- If registration fails, check that the SQL commands ran successfully
- The application should work immediately after database setup

That's it! Once you run the SQL command, your AI Calendar Assistant will be fully functional.
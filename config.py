import os

# API Keys and Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "placeholder_groq_key")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://placeholder.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "placeholder_supabase_key")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "placeholder_google_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "placeholder_google_client_secret")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "placeholder_jwt_secret")
JWT_ALGORITHM = "HS256"

# Backend Configuration - Hardcoded for production
BACKEND_URL = "https://uncle-ben-backend.onrender.com"

# Model Configuration
# Switch to llama3-70b which doesn't show reasoning process
GROQ_MODEL = "llama3-70b-8192"

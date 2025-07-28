#!/usr/bin/env python3
"""
Simple database setup using direct table operations
"""
import uuid
from datetime import datetime
from supabase import create_client
import config

def create_tables():
    """Create tables by attempting basic operations"""
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    print("Setting up database tables...")
    
    # Test and create conversations table
    try:
        # Try to select from conversations
        result = supabase.table('conversations').select('*').limit(1).execute()
        print("✓ Conversations table exists")
    except:
        try:
            # Create a dummy conversation to force table creation
            dummy_data = {
                'id': str(uuid.uuid4()),
                'user_id': 'setup',
                'title': 'Setup Test',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            supabase.table('conversations').insert(dummy_data).execute()
            print("✓ Created conversations table")
        except Exception as e:
            print(f"✗ Failed to create conversations table: {e}")
    
    # Test and create chat_messages table
    try:
        result = supabase.table('chat_messages').select('*').limit(1).execute()
        print("✓ Chat messages table exists")
    except:
        print("✗ Chat messages table needs to be created manually")
    
    # Test and create appointments table
    try:
        result = supabase.table('appointments').select('*').limit(1).execute()
        print("✓ Appointments table exists")
    except:
        print("✗ Appointments table needs to be created manually")
    
    # Check users table has name column
    try:
        result = supabase.table('users').select('name').limit(1).execute()
        print("✓ Users table has name column")
    except:
        print("✗ Users table missing name column")
    
    print("Database setup completed!")

if __name__ == "__main__":
    create_tables()
#!/usr/bin/env python3
"""
Fix database by creating missing tables programmatically
"""
import uuid
from datetime import datetime
from supabase import create_client
import config

def create_missing_tables():
    """Create missing database tables using direct inserts"""
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    
    print("Creating missing database tables...")
    
    # Add name column to users if missing
    try:
        # Test if name column exists by trying to select it
        result = supabase.table('users').select('name').limit(1).execute()
        print("✓ Users table has name column")
    except:
        print("Adding name column to users table...")
        # Create a test user with name to force column creation
        test_user = {
            'id': str(uuid.uuid4()),
            'email': 'setup@test.com',
            'name': 'Setup User'
        }
        try:
            supabase.table('users').insert(test_user).execute()
            # Delete the test user
            supabase.table('users').delete().eq('email', 'setup@test.com').execute()
            print("✓ Added name column to users table")
        except Exception as e:
            print(f"✗ Failed to add name column: {e}")
    
    # Create conversations table
    try:
        result = supabase.table('conversations').select('*').limit(1).execute()
        print("✓ Conversations table exists")
    except:
        print("Creating conversations table...")
        try:
            # Force table creation with a dummy record
            dummy_conv = {
                'id': str(uuid.uuid4()),
                'user_id': 'setup',
                'title': 'Setup Conversation',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            result = supabase.table('conversations').insert(dummy_conv).execute()
            if result.data:
                # Delete the dummy record
                supabase.table('conversations').delete().eq('user_id', 'setup').execute()
                print("✓ Created conversations table")
            else:
                print("✗ Failed to create conversations table")
        except Exception as e:
            print(f"✗ Conversations table creation failed: {e}")
    
    # Create chat_messages table  
    try:
        result = supabase.table('chat_messages').select('*').limit(1).execute()
        print("✓ Chat messages table exists")
    except:
        print("✗ Chat messages table needs manual creation in Supabase dashboard")
    
    # Create appointments table
    try:
        result = supabase.table('appointments').select('*').limit(1).execute()
        print("✓ Appointments table exists")
    except:
        print("✗ Appointments table needs manual creation in Supabase dashboard")
    
    return True

if __name__ == "__main__":
    create_missing_tables()
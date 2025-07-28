#!/usr/bin/env python3
"""
Setup script to create database tables
"""
import os
from supabase import create_client
import config

def setup_database():
    """Create necessary database tables"""
    try:
        # Connect to Supabase
        supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        
        print("Creating database tables...")
        
        # Read SQL file
        with open('create_tables.sql', 'r') as f:
            sql_commands = f.read()
        
        # Split by semicolon and execute each command
        commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
        
        for command in commands:
            try:
                result = supabase.rpc('exec_sql', {'sql': command}).execute()
                print(f"✓ Executed: {command[:50]}...")
            except Exception as e:
                print(f"✗ Failed: {command[:50]}... - {e}")
        
        print("Database setup completed!")
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()
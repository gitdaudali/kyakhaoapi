#!/usr/bin/env python3
"""
Django Cup Streaming Application Startup Script
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Cup Streaming Django Application...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔧 Admin panel: http://localhost:8000/admin")
    print("📚 API Documentation: http://localhost:8000/api/v1/")
    print("=" * 50)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Run migrations first
    print("🔄 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Start the development server
    print("🌐 Starting Django development server...")
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])

#!/usr/bin/env python3
"""
Cup Streaming Projects Startup Script
Choose which project to run: Django or FastAPI
"""

import sys
import os
import subprocess

def start_django():
    """Start Django project"""
    print("🚀 Starting Django project...")
    os.chdir('django')
    subprocess.run([sys.executable, 'start_django.py'])

def start_fastapi():
    """Start FastAPI project"""
    print("🚀 Starting FastAPI project...")
    os.chdir('fastapi')
    subprocess.run([sys.executable, 'start_fastapi.py'])

def main():
    print("=" * 60)
    print("🎬 Cup Streaming Platform - Project Launcher")
    print("=" * 60)
    print("Choose which project to start:")
    print("1. Django Project (Port 8000)")
    print("2. FastAPI Project (Port 8001)")
    print("3. Exit")
    print("=" * 60)
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            start_django()
            break
        elif choice == '2':
            start_fastapi()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

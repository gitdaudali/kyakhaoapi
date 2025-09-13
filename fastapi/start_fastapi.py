#!/usr/bin/env python3
"""
FastAPI Cup Streaming Application Startup Script
"""

import os
import sys

import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Cup Streaming FastAPI Application...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("📖 ReDoc: http://localhost:8001/redoc")
    print("🎨 Custom Swagger: http://localhost:8001/static/swagger-ui.html")
    print("=" * 50)

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, log_level="info")

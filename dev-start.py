#!/usr/bin/env python3
"""
Development server startup script for Office Attendance Backend
"""
import subprocess
import sys
import os

def start_server():
    """Start the FastAPI development server"""
    print("🚀 Starting Office Attendance Backend...")
    print("📍 Server will be available at: http://localhost:8080")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Change to backend directory if not already there
        if not os.path.exists('main.py'):
            print("❌ Error: main.py not found. Make sure you're in the backend directory.")
            sys.exit(1)
        
        # Start uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "localhost", 
            "--port", "8080"
        ])
    except KeyboardInterrupt:
        print("\n✅ Server stopped successfully!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 
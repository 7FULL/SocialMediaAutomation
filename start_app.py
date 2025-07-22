#!/usr/bin/env python3
"""
Social Media Automation Web Application Launcher
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    """Launch the Social Media Automation Web Application"""
    
    print("🚀 Starting Social Media Automation Web Application...")
    
    # Change to the project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ Backend dependencies found")
    except ImportError:
        print("❌ Backend dependencies missing. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "web_app/backend/requirements.txt"])
    
    # Check if frontend is built
    frontend_build = project_root / "web_app" / "frontend" / "build"
    if not frontend_build.exists():
        print("⚠️  Frontend not built. Please run:")
        print("   cd web_app/frontend")
        print("   npm install")
        print("   npm run build")
        print()
        print("For now, starting backend only...")
    else:
        print("✅ Frontend build found")
    
    # Start the backend server
    backend_path = project_root / "web_app" / "backend"
    os.chdir(backend_path)
    
    print("🌐 Starting backend server on http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/api/docs")
    print("🎯 Web Application: http://localhost:8000")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the FastAPI server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
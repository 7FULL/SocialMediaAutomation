#!/usr/bin/env python3
"""
Social Media Automation Web Application Server
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)
    
    # Start backend in a new cmd tab
    if os.name == 'nt':  # Windows
        subprocess.Popen(['start', 'cmd', '/k', 'python', 'main.py'], shell=True)
    else:  # Linux/Mac
        subprocess.Popen(['gnome-terminal', '--tab', '--', 'python3', 'main.py'])


def start_frontend():
    """Start the React frontend development server"""
    print("🌀 Starting frontend server...")
    frontend_path = Path(__file__).parent / "frontend"
    os.chdir(frontend_path)
    
    # Start frontend in a new cmd tab
    if os.name == 'nt':  # Windows
        subprocess.Popen(['start', 'cmd', '/k', 'npm', 'start'], shell=True)
    else:  # Linux/Mac
        subprocess.Popen(['gnome-terminal', '--tab', '--', 'npm', 'start'])


def main():
    """Main function to start both servers"""
    print("🌟 Social Media Automation Suite v2.0")
    print("=====================================")
    
    # Start both servers
    start_backend()
    time.sleep(2)  # Wait a bit before starting frontend
    start_frontend()
    
    print("✅ Both servers started successfully!")
    print("📱 Backend: http://localhost:8000")
    print("🌐 Frontend: http://localhost:3000")
    print("Press Ctrl+C to stop this script (servers will continue running)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Script stopped. Servers are still running in separate windows.")


if __name__ == "__main__":
    main()
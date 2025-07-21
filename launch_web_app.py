#!/usr/bin/env python3
"""
Simple launcher for Social Media Automation Web Application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def install_backend_dependencies():
    """Install backend Python dependencies"""
    print("📦 Installing backend dependencies...")
    requirements_file = Path("web_app/backend/requirements.txt")
    
    if requirements_file.exists():
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            print("✅ Backend dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install backend dependencies")
            return False
    else:
        print("⚠️  Backend requirements.txt not found")
    
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    
    backend_dir = Path("web_app/backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start uvicorn server
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
        print("✅ Backend server started on http://localhost:8000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def check_node_and_npm():
    """Check if Node.js and npm are available"""
    try:
        subprocess.check_output(["node", "--version"], stderr=subprocess.DEVNULL)
        subprocess.check_output(["npm", "--version"], stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_frontend_dependencies():
    """Install frontend Node.js dependencies"""
    print("📦 Installing frontend dependencies...")
    
    frontend_dir = Path("web_app/frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    if not check_node_and_npm():
        print("❌ Node.js and npm are required for the frontend")
        print("Please install Node.js from https://nodejs.org/")
        return False
    
    try:
        os.chdir(frontend_dir)
        subprocess.check_call(["npm", "install"])
        print("✅ Frontend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install frontend dependencies")
        return False

def start_frontend():
    """Start the React frontend"""
    print("🎨 Starting frontend development server...")
    
    frontend_dir = Path("web_app/frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        os.chdir(frontend_dir)
        
        # Start React development server
        subprocess.Popen(["npm", "start"])
        
        print("✅ Frontend server started on http://localhost:3000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main launcher function"""
    print("🌟 Social Media Automation Suite v2.0")
    print("=====================================")
    print()
    
    # Remember original directory
    original_dir = os.getcwd()
    
    try:
        # Install backend dependencies
        if not install_backend_dependencies():
            return 1
        
        # Start backend
        os.chdir(original_dir)
        if not start_backend():
            return 1
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Install frontend dependencies
        os.chdir(original_dir)
        if not install_frontend_dependencies():
            print("⚠️  Frontend not available, but backend is running")
            print("🌐 You can access the API at http://localhost:8000/api/docs")
            return 0
        
        # Start frontend
        os.chdir(original_dir)
        if not start_frontend():
            print("⚠️  Frontend failed to start, but backend is running")
            print("🌐 You can access the API at http://localhost:8000/api/docs")
            return 0
        
        # Wait for frontend to start
        print("⏳ Waiting for frontend to start...")
        time.sleep(5)
        
        # Open browser
        print("🌐 Opening web application in browser...")
        webbrowser.open("http://localhost:3000")
        
        print()
        print("✅ Application launched successfully!")
        print("🌐 Web App: http://localhost:3000")
        print("📖 API Docs: http://localhost:8000/api/docs")
        print("🔑 Login: admin / admin123")
        print()
        print("Press Ctrl+C to stop the servers")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            return 0
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    sys.exit(main())
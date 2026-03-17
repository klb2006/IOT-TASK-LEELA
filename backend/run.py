#!/usr/bin/env python3
"""
Launcher for FastAPI app - handles module discovery across different Python environments.
"""
import os
import sys
import subprocess

# Ensure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

try:
    import uvicorn
    from main import app
except ImportError as e:
    print(f"ERROR: {e}")
    print(f"Python: {sys.executable}")
    print(f"Path: {sys.path}")
    print("\nAttempting to install missing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    # Try import again
    import uvicorn
    from main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=port,
        log_level='info'
    )

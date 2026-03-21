#!/usr/bin/env python3
"""
Launcher for FastAPI app - handles module discovery across different Python environments.
"""
import os
import sys
import subprocess
import site

# Ensure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

# Add all possible site-packages locations to path
site.addsitedir('/opt/render/.local/lib/python3.11/site-packages')
site.addsitedir('/usr/local/lib/python3.11/dist-packages')
site.addsitedir('/usr/lib/python3/dist-packages')
sys.path.extend([
    '/opt/render/.local/lib/python3.11/site-packages',
    '/usr/local/lib/python3.11/dist-packages',
    '/usr/lib/python3/dist-packages'
])

try:
    import uvicorn
    from main import app
except ImportError as e:
    print(f"ERROR: {e}")
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Path: {sys.path}")
    print("\nAttempting to install missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Install failed with status {e.returncode}. Retrying...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])
    
    # Reload site packages after installation
    site.addsitedir('/opt/render/.local/lib/python3.11/site-packages')
    sys.path.insert(0, '/opt/render/.local/lib/python3.11/site-packages')
    
    # Try import again
    import uvicorn
    from main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting FastAPI server on 0.0.0.0:{port}")
    print(f"Using Python: {sys.executable}")
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=port,
        log_level='info'
    )

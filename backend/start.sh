#!/bin/bash
set -e

# Set up environment
export PYTHONUNBUFFERED=1

# Add all possible site-packages to PYTHONPATH
export PYTHONPATH="/opt/render/.local/lib/python3.11/site-packages:/usr/local/lib/python3.11/dist-packages:/usr/lib/python3.11/site-packages:/usr/lib/python3/dist-packages:/opt/render/project/src/backend:$PYTHONPATH"

cd /opt/render/project/src/backend

# Execute the launcher
exec python3 run.py

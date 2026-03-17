#!/bin/bash
set -e

# Set up environment
export PYTHONUNBUFFERED=1
cd /opt/render/project/src/backend

# Make sure pip packages are accessible
export PYTHONPATH=/opt/render/project/src/backend:$PYTHONPATH

# Execute the launcher
python3 run.py

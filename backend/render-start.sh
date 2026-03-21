#!/bin/bash
# Render deployment start script

# Install Python dependencies
pip install -r requirements.txt

# Run migrations/setup if needed
# python sync.py

# Start the FastAPI server
exec uvicorn main:app --host 0.0.0.0 --port $PORT

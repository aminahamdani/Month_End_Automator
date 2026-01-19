#!/bin/bash
# Azure App Service startup script for Linux

# Activate virtual environment if it exists
if [ -d "antenv" ]; then
  source antenv/bin/activate
fi

# Start the FastAPI application with uvicorn
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600

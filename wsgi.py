#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from api import app

# For WSGI compatibility, we need to expose the app
application = app

# Also expose as 'app' for compatibility
app = application

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

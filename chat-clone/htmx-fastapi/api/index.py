"""
Vercel serverless function entry point.
Wraps the FastAPI app for Vercel deployment.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set working directory for templates
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects the app to be named 'app' or 'handler'
handler = app

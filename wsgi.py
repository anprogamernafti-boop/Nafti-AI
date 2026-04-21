#!/usr/bin/env python
"""
WSGI entry point for Gunicorn on HF Spaces
This ensures the app starts quickly for health checks
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import and get the Flask app
try:
    from server import app
    print("[WSGI] Successfully loaded Flask app from server module")
except ImportError as e:
    print(f"[WSGI] ERROR: Could not import app from server: {e}")
    sys.exit(1)

# Expose app as the WSGI application
if __name__ != "__main__":
    print("[WSGI] WSGI app ready!")

__all__ = ['app']

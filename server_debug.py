#!/usr/bin/env python
"""
Flask app with aggressive error handling to identify deadlock causes
"""
import sys
import signal
import logging

# Set up logging FIRST before any other imports
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

print("[INIT] Starting Nafti AI server initialization...")

# Timeout handler
def timeout_handler(signum, frame):
    print("[ERROR] Timeout during import - deadlock detected!")
    sys.exit(1)

# Set a 10-second timeout for the entire import process
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)

try:
    print("[IMPORT] Loading Flask...")
    from flask import Flask, request, jsonify, render_template, session, redirect, url_for
    print("[IMPORT] ✅ Flask loaded")
    
    print("[IMPORT] Loading CORS...")
    from flask_cors import CORS
    print("[IMPORT] ✅ CORS loaded")
    
    print("[IMPORT] Loading dotenv...")
    from dotenv import load_dotenv
    print("[IMPORT] ✅ dotenv loaded")
    
    print("[IMPORT] Loading standard libraries...")
    import os
    import json
    import hashlib
    import uuid
    import base64
    import time
    import gc
    from pathlib import Path
    from PIL import Image
    from io import BytesIO
    print("[IMPORT] ✅ Standard libraries loaded")
    
    # Cancel the timeout since imports succeeded
    signal.alarm(0)
    
except Exception as e:
    print(f"[ERROR] Import failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Now we're safe to proceed
print("[INIT] Creating Flask app...")
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecret')
CORS(app)

print("[INIT] Flask app created successfully")

# --- HEALTH ENDPOINTS (these MUST work) ---
@app.route("/health", methods=["GET", "HEAD"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/healthz", methods=["GET", "HEAD"])  
def healthz():
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Nafti AI is running"}), 200

print("[INIT] ✅ Health endpoints registered")

# --- Google OAuth (safe import) ---
try:
    print("[INIT] Loading Google OAuth...")
    from flask_dance.contrib.google import make_google_blueprint, google
    
    if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'):
        google_bp = make_google_blueprint(
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scope=["profile", "email"],
            redirect_url="/google_callback"
        )
        app.register_blueprint(google_bp, url_prefix="/login")
        print("[INIT] ✅ Google OAuth configured")
    else:
        print("[INIT] ⚠️  Google OAuth credentials missing")
except Exception as e:
    print(f"[INIT] ⚠️  Google OAuth error (not critical): {e}")

print("[INIT] ✅ Application fully initialized and ready!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)

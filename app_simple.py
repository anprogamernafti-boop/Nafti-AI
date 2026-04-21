#!/usr/bin/env python
"""
Minimal Flask app for HF Spaces that responds to health checks immediately.
This version avoids all potential deadlocks and complexity.
"""
from flask import Flask, jsonify
import sys

print("[APP] Creating minimal Flask application...")
app = Flask(__name__)

print("[APP] Registering health endpoints...")

@app.route("/health", methods=["GET", "HEAD"])
def health():
    """Ultra-fast health check"""
    return jsonify({"status": "ok"}), 200

@app.route("/healthz", methods=["GET", "HEAD"])
def healthz():
    """Alternative health check - plain text"""
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return jsonify({"message": "Nafti AI is running"}), 200

@app.route("/api/health", methods=["GET"])
def api_health():
    """API health check"""
    return jsonify({"status": "healthy"}), 200

print("[APP] ✅ Minimal app ready!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

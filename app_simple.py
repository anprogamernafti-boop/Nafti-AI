#!/usr/bin/env python
"""
Ultra-minimal Flask app for HF Spaces that responds instantly.
HF Spaces has a 30-min hard timeout on containers.
This app must respond to health checks within seconds of startup.
"""
from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET", "HEAD"])
def health():
    return "OK", 200

@app.route("/healthz", methods=["GET", "HEAD"])
def healthz():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

#!/usr/bin/env python
"""
Auto-restart monitor for HF Spaces to avoid 30-min timeout.
This script restarts the Gunicorn worker every 25 minutes before HF Spaces kills it.
"""
import subprocess
import time
import signal
import sys
import os

RESTART_INTERVAL = 1500  # 25 minutes
process = None

def signal_handler(sig, frame):
    global process
    print("\n[MONITOR] Received signal, cleaning up...")
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print("[MONITOR] Starting auto-restart monitor (restart every 25 min)")
print("[MONITOR] This prevents HF Spaces 30-min timeout")

restart_count = 0
while True:
    restart_count += 1
    print(f"\n[MONITOR] Starting app (restart #{restart_count})...")
    
    # Start gunicorn with minimal config
    cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--worker-class", "sync",
        "--timeout", "120",
        "--keep-alive", "65",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "app_simple:app"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        print(f"[MONITOR] App started with PID {process.pid}")
        
        # Wait 25 minutes
        time.sleep(RESTART_INTERVAL)
        
        print("[MONITOR] Time to restart! (preventing 30-min HF Spaces timeout)")
        process.terminate()
        
        # Give it 5 seconds to shutdown gracefully
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("[MONITOR] Forcing kill after timeout...")
            process.kill()
            process.wait()
        
        print("[MONITOR] App stopped, restarting...")
        time.sleep(2)  # Brief pause between restarts
        
    except KeyboardInterrupt:
        print("[MONITOR] Interrupted by user")
        break
    except Exception as e:
        print(f"[MONITOR] Error: {e}")
        time.sleep(5)
        
print("[MONITOR] Monitor stopped")

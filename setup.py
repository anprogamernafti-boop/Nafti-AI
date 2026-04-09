#!/usr/bin/env python
"""
Setup script for Nafti AI - handles PyTorch installation with correct index URL
Run this after pip install -r requirements.txt to complete the setup
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report success/failure"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {description} successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         Nafti AI - Complete Installation Setup             ║
║  (NOTE: Run this AFTER creating venv and before running    ║
║   pip install -r requirements.txt)                         ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Install base requirements (without torch)
    print("\n📋 Step 1: Installing base requirements...")
    cmd1 = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    if not run_command(cmd1, "Base requirements installation"):
        print("\n⚠️ Base requirements installation failed. Fix the errors above and retry.")
        return False
    
    # Step 2: Install PyTorch (CPU)
    print("\n📋 Step 2: Installing PyTorch (CPU-only)...")
    print("           If you have an NVIDIA GPU and want CUDA acceleration,")
    print("           manually run: pip install torch --index-url https://download.pytorch.org/whl/cu118")
    
    cmd2 = [
        sys.executable, "-m", "pip", "install",
        "torch", "--index-url", "https://download.pytorch.org/whl/cpu"
    ]
    if not run_command(cmd2, "PyTorch CPU installation"):
        print("\n⚠️ PyTorch installation failed.")
        print("   See: https://pytorch.org/get-started/locally/")
        return False
    
    # Step 3: Verify installation
    print("\n📋 Step 3: Verifying installation...")
    try:
        import torch
        import diffusers
        import transformers
        import accelerate
        print(f"✅ Torch version: {torch.__version__}")
        print(f"✅ Diffusers installed")
        print(f"✅ Transformers installed")
        print(f"✅ Accelerate installed")
    except ImportError as e:
        print(f"❌ Import verification failed: {e}")
        return False
    
    # Final message
    print(f"""
╔════════════════════════════════════════════════════════════╗
║              ✅ Setup Complete!                            ║
╚════════════════════════════════════════════════════════════╝

Next steps:

1. Enable local image generation:
   Edit .env and set:   USE_LOCAL=1

2. Start the server:
   python server.py

3. Test image generation:
   python check_setup.py

4. First image generation will download ~4GB of model data
   and take 2-5 minutes. Subsequent generations are much faster.

Tip: Run 'python check_setup.py' anytime to verify your setup!
    """)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

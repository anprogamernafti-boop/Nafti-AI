#!/usr/bin/env python
"""
Quick test and status check for Nafti AI image generation setup
"""

import sys

def check_imports():
    print("=" * 60)
    print("CHECKING DEPENDENCIES FOR IMAGE GENERATION")
    print("=" * 60)
    
    # check architecture
    import platform, sys
    arch = platform.architecture()[0]
    is64 = sys.maxsize > 2**32
    print(f"Python architecture: {arch} (64-bit? {is64})")
    if not is64:
        print("⚠️  32-bit Python detected; local generation will not work. Install 64-bit Python.")
    
    checks = {
        "torch": "PyTorch (Core ML framework)",
        "diffusers": "Hugging Face Diffusers (Stable Diffusion)",
        "transformers": "Hugging Face Transformers",
        "accelerate": "Accelerate (faster inference)",
    }
    
    available = {}
    for pkg, desc in checks.items():
        try:
            __import__(pkg)
            available[pkg] = True
            print(f"✅ {pkg:15} - {desc}")
        except ImportError:
            available[pkg] = False
            print(f"❌ {pkg:15} - {desc}")
    
    print("\n" + "=" * 60)
    print("IMAGE GENERATION OPTIONS")
    print("=" * 60)
    
    # Check configuration
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    providers = {
        "Local (Stable Diffusion v1.5)": {
            "env": "USE_LOCAL",
            "required": ["torch", "diffusers", "transformers", "accelerate"],
            "notes": "Free, runs on your machine, ~4GB model download"
        },
        "Replicate (Cloud)": {
            "env": "REPLICATE_API_TOKEN",
            "required": [],
            "notes": "Paid ($1-5/month), reliable, fast"
        },
        "Gemini (Google)": {
            "env": "GEMINI_API_KEY",
            "required": [],
            "notes": "Paid after free tier, rate-limited"
        },
        "Pollinations.ai (Free Cloud)": {
            "env": "USE_POLLINATIONS",
            "required": [],
            "notes": "Free but unreliable (50% success)"
        },
    }
    
    for provider, config in providers.items():
        check_pass = True
        
        # Check if enabled
        if config["env"] in ["USE_LOCAL", "USE_POLLINATIONS"]:
            enabled = os.getenv(config["env"], "0") in ("1", "true", "True")
            status = "✅ ENABLED" if enabled else "⭕ Disabled"
        else:
            key = os.getenv(config["env"], "")
            enabled = bool(key)
            status = f"✅ ENABLED" if enabled else "⭕ No key"
        
        # Check dependencies
        missing = []
        for req in config["required"]:
            if not available.get(req):
                missing.append(req)
                check_pass = False
        
        print(f"\n{provider}")
        print(f"  Status: {status}")
        if missing:
            print(f"  ⚠️  Missing: {', '.join(missing)}")
        else:
            print(f"  ✅ All dependencies available")
        print(f"  {config['notes']}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if available.get("torch") and available.get("diffusers"):
        print("\n✅ Local generation is ready! Set USE_LOCAL=1 in .env")
        print("   First image will take ~2-5 min (model download), then much faster")
    else:
        print("\n⚠️  Local generation not available. Options:")
        print("   1. Install: pip install torch diffusers transformers accelerate")
        print("   2. Use cloud provider (Replicate, Gemini, Pollinations)")
        print("   3. Current fallback: Pollinations.ai (unreliable)")
    
    print("\n" + "=" * 60)
    print("TEST IMAGE GENERATION")
    print("=" * 60)
    
    try:
        import server
        app = server.app
        
        with app.test_client() as client:
            # Set up fake session
            with client.session_transaction() as sess:
                sess['user'] = 'test@example.com'
            
            print("\nTesting /api/generate-image endpoint...")
            res = client.post('/api/generate-image', json={'prompt': 'a cat'})
            
            if res.status_code == 200:
                print("✅ Image generated successfully!")
                data = res.get_json()
                print(f"   Source: {data.get('source')}")
                print(f"   Size: {len(data.get('image_base64', ''))} bytes")
            else:
                print(f"❌ Failed with status {res.status_code}")
                data = res.get_json()
                print(f"   Error: {data.get('error')}")
                if 'details' in data:
                    for service, err in data['details'].items():
                        print(f"     - {service}: {err[:100]}...")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    check_imports()

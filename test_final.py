#!/usr/bin/env python3
"""Final test for language detection fix"""
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

def test_language_detection():
    print("="*70)
    print("LANGUAGE DETECTION TEST - Final Validation")
    print("="*70)
    
    # Load user from users.json
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    if not users:
        print("ERROR: No users in users.json")
        return False
    
    user_email = list(users.keys())[0]
    user_password = users[user_email]
    
    print(f"\nUser: {user_email}")
    
    # Create a proper session
    session = requests.Session()
    session.verify = False
    
    # Step 1: Login
    print("\n[Step 1] Authenticating...")
    login_response = session.post(
        'https://127.0.0.1:5000/login',
        json={
            'email': user_email,
            'password': user_password
        },
        timeout=10
    )
    print(f"  Status: {login_response.status_code}")
    print(f"  Cookies: {session.cookies.get_dict()}")
    
    if login_response.status_code not in [200, 302]:
        print(f"  WARNING: Login may have failed")
        print(f"  Response: {login_response.text[:200]}")
    
    # Step 2: Test English
    print("\n[Step 2] Testing English: 'how are you ?'")
    print("  Sending request...")
    
    try:
        response = session.post(
            'https://127.0.0.1:5000/api/ai',
            json={
                'message': 'how are you ?',
                'history': []
            },
            timeout=45
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '').lower()
            
            print(f"\n  AI Response (first 300 chars):")
            print(f"  {data.get('response', '')[:300]}...\n")
            
            # Check language indicators
            english_markers = ['i am', "i'm", 'doing', 'well', 'fine', 'good', 'great', 'thank', 'hello']
            french_markers = ['je suis', 'très', 'bien', 'merci', 'bonjour', 'comment', 'ça va']
            
            english_count = sum(1 for m in english_markers if m in ai_response)
            french_count = sum(1 for m in french_markers if m in ai_response)
            
            print(f"  English markers found: {english_count}")
            print(f"  French markers found: {french_count}")
            
            if english_count > french_count:
                print("  ✅ RESULT: Response is in ENGLISH")
                return True
            elif french_count > english_count:
                print("  ❌ RESULT: Response is in FRENCH (BUG NOT FIXED)")
                return False
            else:
                print("  ⚠️  RESULT: Language unclear")
                return None
        else:
            print(f"  ERROR: {response.status_code}")
            print(f"  Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == '__main__':
    result = test_language_detection()
    print("\n" + "="*70)
    if result is True:
        print("CONCLUSION: Bug is FIXED! ✅")
    elif result is False:
        print("CONCLUSION: Bug is NOT fixed! ❌")
    else:
        print("CONCLUSION: Test inconclusive")
    print("="*70)

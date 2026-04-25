#!/usr/bin/env python3
"""Test if language detection fix works"""
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print("="*60)
print("TEST: Language Detection Fix")
print("="*60)

# Load users
with open('users.json', 'r') as f:
    users = json.load(f)
    user_email = list(users.keys())[0]
    user_pass = users[user_email]

# Create session
s = requests.Session()
s.verify = False

# Login
print("\nLogging in...")
s.post('https://127.0.0.1:5000/login',
       json={'email': user_email, 'password': user_pass})

# Test English
print("\n[TEST 1] English: 'how are you ?'")
r = s.post('https://127.0.0.1:5000/api/ai',
           json={'message': 'how are you ?', 'history': []})
if r.status_code == 200:
    resp = r.json()['response'].lower()
    if any(w in resp for w in ['i am', 'i\'m', 'doing', 'well', 'fine', 'good']):
        print("✅ ENGLISH RESPONSE DETECTED")
    elif any(w in resp for w in ['je suis', 'bien', 'comment', 'merci']):
        print("❌ FRENCH RESPONSE (BUG NOT FIXED)")
    else:
        print("⚠️  UNCLEAR")
    print(f"Response: {r.json()['response'][:200]}...")
else:
    print(f"ERROR: {r.status_code}")

# Test French
print("\n[TEST 2] French: 'comment allez-vous ?'")
r = s.post('https://127.0.0.1:5000/api/ai',
           json={'message': 'comment allez-vous ?', 'history': []})
if r.status_code == 200:
    resp = r.json()['response'].lower()
    if any(w in resp for w in ['je suis', 'je suis', 'bien', 'merci', 'enchanté']):
        print("✅ FRENCH RESPONSE DETECTED")
    elif any(w in resp for w in ['i am', 'i\'m', 'doing']):
        print("❌ ENGLISH RESPONSE (BUG NOT FIXED)")
    else:
        print("⚠️  UNCLEAR")
    print(f"Response: {r.json()['response'][:200]}...")
else:
    print(f"ERROR: {r.status_code}")

print("\n" + "="*60)

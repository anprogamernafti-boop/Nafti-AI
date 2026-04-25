import requests
import json
import warnings
from urllib.parse import urljoin

# Ignore SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Create a session to maintain cookies
session = requests.Session()
session.verify = False

try:
    base_url = 'https://127.0.0.1:5000'
    
    # Step 1: Try to create/authenticate a test user
    email = 'test@example.com'
    password = 'test123456'
    
    print('Step 1: Attempting to sign up / authenticate test user...')
    print('Email:', email)
    print('-' * 60)
    
    # Try signup first
    signup_url = urljoin(base_url, '/signup')
    signup_data = {
        'email': email,
        'password': password
    }
    
    response = session.post(signup_url, data=signup_data, timeout=10)
    print('Signup attempt - Status:', response.status_code)
    
    # If user already exists, try login
    if response.status_code != 200 and response.status_code != 302:
        print('User might already exist, trying login...')
        login_url = urljoin(base_url, '/login')
        login_data = {
            'email': email,
            'password': password
        }
        response = session.post(login_url, data=login_data, timeout=10)
        print('Login attempt - Status:', response.status_code)
    
    print('Session cookies:', dict(session.cookies))
    print('-' * 60)
    
    # Step 2: Test the language detection endpoint
    print('Step 2: Testing language detection endpoint...')
    api_url = urljoin(base_url, '/api/ai')
    
    payload = {
        'prompt': 'how are you ?'
    }
    
    print('API URL:', api_url)
    print('Payload:', json.dumps(payload, indent=2))
    print('-' * 60)
    
    response = session.post(api_url, json=payload, timeout=10)
    
    print('Status Code:', response.status_code)
    print('Response Headers:', dict(response.headers))
    print('-' * 60)
    
    if response.status_code == 200:
        data = response.json()
        print('Response Body (formatted):')
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Extract and display key information
        print('-' * 60)
        print('EXTRACTED RESULTS:')
        if 'language' in data:
            lang = data['language']
            print('Detected Language:', lang)
        if 'response' in data:
            resp = data['response']
            print('AI Response:', resp)
        if 'error' in data:
            print('Error:', data['error'])
    else:
        print('Error: Status code', response.status_code)
        print('Response text:', response.text)
        
except Exception as e:
    print('Error:', type(e).__name__, str(e))
    import traceback
    traceback.print_exc()

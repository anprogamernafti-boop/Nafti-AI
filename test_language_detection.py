import requests
import json
import warnings

# Ignore SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

try:
    # Test the language detection endpoint
    url = 'https://127.0.0.1:5000/api/ai'
    
    payload = {
        'prompt': 'how are you ?'
    }
    
    print('Testing Flask server language detection...')
    print(f'URL: {url}')
    print(f'Payload: {json.dumps(payload, indent=2)}')
    print('-' * 60)
    
    # Send POST request with verify=False to ignore SSL
    response = requests.post(url, json=payload, verify=False, timeout=10)
    
    print(f'Status Code: {response.status_code}')
    print(f'Response Headers: {dict(response.headers)}')
    print('-' * 60)
    
    if response.status_code == 200:
        data = response.json()
        print('Response Body:')
        print(json.dumps(data, indent=2))
        
        # Extract and display key information
        print('-' * 60)
        print('EXTRACTED RESULTS:')
        if 'language' in data:
            print(f'Detected Language: {data["language"]}')
        if 'response' in data:
            print(f'AI Response: {data["response"]}')
        if 'error' in data:
            print(f'Error: {data["error"]}')
    else:
        print(f'Error: Status code {response.status_code}')
        print(f'Response text: {response.text}')
        
except requests.exceptions.ConnectionError:
    print('Error: Could not connect to server at https://127.0.0.1:5000')
    print('   Make sure the Flask server is running.')
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')

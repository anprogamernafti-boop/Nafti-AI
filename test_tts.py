#!/usr/bin/env python
import requests
import warnings

warnings.filterwarnings('ignore')

url = 'https://127.0.0.1:5000/api/synthesize'
data = {'text': 'Bonjour, comment allez-vous?', 'lang': 'fr'}

try:
    response = requests.post(url, json=data, verify=False, timeout=10)
    print(f'Status Code: {response.status_code}')
    print(f'Content Type: {response.headers.get("Content-Type")}')
    print(f'Audio Size: {len(response.content)} bytes')
    if response.status_code == 200:
        with open('test_audio.mp3', 'wb') as f:
            f.write(response.content)
        print('✅ Audio saved to test_audio.mp3')
    else:
        print(f'Error: {response.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

import requests

s = requests.Session()
base = 'http://127.0.0.1:5000'

try:
    r = s.get(base + '/')
    print('GET / status', r.status_code)
except Exception as e:
    print('error', e)

# use test user on server side via login or fake cookie (skipped)
# further endpoint tests require a running server with proper session state;
# we will just demonstrate structure here.

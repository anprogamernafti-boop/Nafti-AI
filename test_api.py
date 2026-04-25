import requests
import json
import warnings

# Ignore SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Create a session to maintain cookies
session = requests.Session()
session.verify = False

try:
    base_url = 'https://127.0.0.1:5000'
    
    # Step 1: Register user
    email = 'test@example.com'
    password = 'test123456'
    
    print('=' * 60)
    print('ÉTAPE 1: Enregistrement de l''utilisateur')
    print('=' * 60)
    print('Email: ' + email)
    
    register_url = base_url + '/register'
    register_data = {
        'email': email,
        'password': password
    }
    
    response = session.post(register_url, data=register_data, timeout=10, allow_redirects=True)
    print('Tentative de register - Status: ' + str(response.status_code))
    print('URL après redirect: ' + response.url)
    print('Cookies: ' + str(dict(session.cookies)))
    print('-' * 60)
    
    # Step 2: Create a new session for chat
    print()
    print('=' * 60)
    print('ÉTAPE 2: Création d''une nouvelle session de chat')
    print('=' * 60)
    
    session_url = base_url + '/session/new'
    response = session.post(session_url, timeout=10)
    print('Status: ' + str(response.status_code))
    
    session_id = None
    if response.status_code == 200:
        sess_data = response.json()
        print('Réponse: ' + json.dumps(sess_data, indent=2))
        session_id = sess_data.get('id')
    else:
        print('Erreur: ' + response.text[:300])
    
    if not session_id:
        print('Impossible de créer une session')
    else:
        # Step 3: Test the language detection endpoint
        print()
        print('=' * 60)
        print('ÉTAPE 3: Test de l''endpoint /api/ai')
        print('=' * 60)
        
        api_url = base_url + '/api/ai'
        
        # Format messages correctly
        payload = {
            'messages': [
                {
                    'role': 'user',
                    'content': 'how are you ?'
                }
            ],
            'session_id': session_id
        }
        
        print('URL: ' + api_url)
        print('Payload: ' + json.dumps(payload, indent=2))
        print('-' * 60)
        
        response = session.post(api_url, json=payload, timeout=30)
        
        print('Code de status: ' + str(response.status_code))
        print('-' * 60)
        
        if response.status_code == 200:
            data = response.json()
            print('Réponse complète:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extract and display key information
            print()
            print('=' * 60)
            print('RÉSULTATS EXTRAITS:')
            print('=' * 60)
            
            # Get detected language from the session info or the response
            print('Langage détecté: (sera extrait du contexte)')
            
            if 'choices' in data and len(data['choices']) > 0:
                resp_text = data['choices'][0].get('message', {}).get('content', '')
                print('Premiers 200 caractères de la réponse:')
                print(resp_text[:200])
                if len(resp_text) > 200:
                    print('...')
        else:
            print('Erreur: Code de status ' + str(response.status_code))
            try:
                err_data = response.json()
                print('Erreur JSON: ' + json.dumps(err_data, indent=2))
            except:
                print('Réponse: ' + response.text[:500])
        
except Exception as e:
    print('Exception: ' + type(e).__name__ + ': ' + str(e))
    import traceback
    traceback.print_exc()

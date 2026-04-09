import server

PROMPT = "A surreal painting of a cat riding a bicycle"

# individual function tests
for name, func in (
    ("pollinations", server._generate_with_pollinations),
    ("gemini", server._generate_with_gemini),
    ("replicate", server._generate_with_replicate),
    ("huggingface", server._generate_with_huggingface),
):
    print(f"\n{name.capitalize()} test...")
    try:
        result = func(PROMPT)
        print(f"{name} result keys:", result.keys())
    except Exception as e:
        print(f"{name} error:", e)

# attempt HTTP call through Flask test client to exercise pipeline
print("\nTesting /api/generate-image via test client")
app = server.app
with app.test_client() as client:
    # set up fake user session
    with client.session_transaction() as sess:
        sess['user'] = 'test@example.com'

    print("\n-- normal pipeline call --")
    res = client.post('/api/generate-image', json={'prompt': PROMPT})
    print('status', res.status_code)
    print('response', res.get_json())

    # simulate no providers enabled
    print("\n-- simulate no providers configured --")
    # temporarily clear server configuration
    orig_repl = server.REPLICATE_API_TOKEN
    orig_gem = server.GEMINI_API_KEY
    orig_hf = server.USE_HUGGINGFACE
    orig_poll = server.USE_POLLINATIONS
    server.REPLICATE_API_TOKEN = ''
    server.GEMINI_API_KEY = ''
    server.USE_HUGGINGFACE = False
    server.USE_POLLINATIONS = False

    res2 = client.post('/api/generate-image', json={'prompt': PROMPT})
    print('status', res2.status_code)
    print('response', res2.get_json())

    # restore
    server.REPLICATE_API_TOKEN = orig_repl
    server.GEMINI_API_KEY = orig_gem
    server.USE_HUGGINGFACE = orig_hf
    server.USE_POLLINATIONS = orig_poll

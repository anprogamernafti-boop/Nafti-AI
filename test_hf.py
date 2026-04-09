import server

PROMPT = "A cat on a bicycle"

print('Testing Hugging Face...')
try:
    result = server._generate_with_huggingface(PROMPT)
    print('Success:', result.keys())
except Exception as e:
    print('Error:', e)
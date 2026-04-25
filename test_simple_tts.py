from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

@app.route('/api/test-synth', methods=['POST'])
def test_synthesize():
    """Test synthesize endpoint"""
    print("[TEST] Request received")
    try:
        from gtts import gTTS
        print("[TEST] gTTS imported")
        
        data = request.get_json()
        text = data.get('text', '').strip()
        lang = data.get('lang', 'fr')
        
        print(f"[TEST] Text: '{text}', Lang: {lang}")
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        
        tts = gTTS(text=text, lang=lang, slow=False)
        print("[TEST] gTTS object created")
        
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        print(f"[TEST] Audio size: {len(audio_buffer.getvalue())} bytes")
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name=None
        )
    except Exception as e:
        print(f"[TEST] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(ssl_context=('server.crt', 'server.key'), host='0.0.0.0', port=5001, debug=False)

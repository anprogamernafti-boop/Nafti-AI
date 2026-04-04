#!/usr/bin/env python3
"""Nafti AI - SDXL Image Generator using Flask"""

from flask import Flask, render_template, request, jsonify
from PIL import Image
import torch
from diffusers import AutoPipelineForText2Image
import io
import base64

app = Flask(__name__)

# Device configuration
device = "cuda" if torch.cuda.is_available() else "cpu"

# Global pipeline cache
pipe = None

def get_pipeline():
    """Lazy load pipeline"""
    global pipe
    if pipe is None:
        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
        )
        pipe = pipe.to(device)
    return pipe

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        width = int(data.get('width', 512))
        height = int(data.get('height', 512))
        steps = int(data.get('steps', 25))
        guidance = float(data.get('guidance', 7.5))
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate image
        pipe = get_pipeline()
        image = pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=guidance,
        ).images[0]
        
        # Convert to base64
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        
        return jsonify({'image': f'data:image/png;base64,{img_base64}'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=False)

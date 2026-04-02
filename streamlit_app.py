#!/usr/bin/env python3
"""Nafti AI - SDXL Image Generator using Gradio"""

import gradio as gr
from PIL import Image
import torch
from diffusers import AutoPipelineForText2Image

# Load once
device = "cuda" if torch.cuda.is_available() else "cpu"

def generate_image(prompt, width, height, steps, guidance):
    """Generate image from prompt"""
    if not prompt:
        return None
    
    # Load model on first use
    pipe = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
    )
    pipe = pipe.to(device)
    
    # Generate
    image = pipe(
        prompt=prompt,
        height=int(height),
        width=int(width),
        num_inference_steps=int(steps),
        guidance_scale=float(guidance),
    ).images[0]
    
    return image

# Build UI
with gr.Blocks(title="Nafti AI") as demo:
    gr.Markdown("# Nafti AI Image Generator")
    gr.Markdown("Free SDXL image generation - powered by Hugging Face Spaces")
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="Describe the image you want...",
                lines=3
            )
            
            with gr.Row():
                width = gr.Slider(256, 1024, 512, step=64, label="Width")
                height = gr.Slider(256, 1024, 512, step=64, label="Height")
            
            with gr.Row():
                steps = gr.Slider(15, 50, 25, label="Steps")
                guidance = gr.Slider(1, 20, 7.5, label="Guidance Scale")
            
            btn = gr.Button("Generate Image", size="lg")
        
        image_out = gr.Image(label="Generated Image")
    
    btn.click(
        generate_image,
        inputs=[prompt, width, height, steps, guidance],
        outputs=image_out
    )
    
    gr.Examples(
        [
            ["A beautiful sunset over mountains, oil painting style", 512, 512, 25, 7.5],
            ["A cozy futuristic cafe, cyberpunk neon lights", 512, 512, 25, 7.5],
        ],
        [prompt, width, height, steps, guidance]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        api_open=False
    )

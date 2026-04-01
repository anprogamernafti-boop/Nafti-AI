#!/usr/bin/env python3
"""
Nafti AI - Streamlit App for HuggingFace Spaces
Free image generation using Stable Diffusion XL (local)
"""

import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import torch

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Streamlit
st.set_page_config(
    page_title="Nafti AI - Image Generation",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        max-width: 800px;
        margin: 0 auto;
    }
    .stButton button {
        width: 100%;
        padding: 12px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎨 Nafti AI Image Generator")
st.markdown("Generate stunning images using Stable Diffusion XL - **100% Free**")
st.divider()

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
st.info(f"🚀 Running on: **{device.upper()}**", icon="ℹ️")

# Import the SDXL generation function
try:
    from diffusers import AutoPipelineForText2Image
    import torch
    
    @st.cache_resource
    def load_pipeline():
        """Load SDXL pipeline (cached)"""
        st.spinner("Loading Stable Diffusion XL model...")
        
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        
        pipeline = AutoPipelineForText2Image.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
            variant="fp16" if device == "cuda" else None
        )
        pipeline = pipeline.to(device)
        
        return pipeline
    
    # Load model
    with st.spinner("Initializing model..."):
        pipeline = load_pipeline()
    
except ImportError:
    st.error("❌ Required libraries not installed. Please install: `pip install diffusers transformers torch accelerate safetensors`")
    sys.exit(1)

# Main input area
st.subheader("📝 Describe Your Image")

prompt = st.text_area(
    "What would you like to generate?",
    placeholder="e.g., 'A beautiful sunset over mountains, oil painting style'",
    height=100
)

# Advanced options (collapsed by default)
with st.expander("⚙️ Advanced Options"):
    col1, col2 = st.columns(2)
    
    with col1:
        width = st.slider("Width", 256, 1024, 512, step=64)
        height = st.slider("Height", 256, 1024, 512, step=64)
    
    with col2:
        num_steps = st.slider("Steps (quality vs speed)", 15, 50, 25)
        guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5)

# Generate button
if st.button("✨ Generate Image", type="primary", use_container_width=True):
    if not prompt.strip():
        st.warning("Please enter a prompt to generate an image.")
    else:
        with st.spinner("🎨 Generating your image... (this may take a minute)"):
            try:
                # Generate image
                image = pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_steps,
                    guidance_scale=guidance_scale,
                    negative_prompt="low quality, blurry, distorted"
                ).images[0]
                
                # Display result
                st.success("✅ Image generated successfully!")
                st.image(image, use_column_width=True)
                
                # Download button
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                st.download_button(
                    label="📥 Download Image",
                    data=buffered.getvalue(),
                    file_name=f"nafti_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                # Show prompt used
                with st.expander("📋 View Prompt"):
                    st.text(prompt)
                    
            except Exception as e:
                st.error(f"❌ Error generating image: {str(e)}")

# Footer
st.divider()
st.markdown("""
---
✨ **Nafti AI** - Free Image Generation Powered by Stable Diffusion XL

🔗 [GitHub](https://github.com) | 📧 Contact

*Generating on CPU? It will be slower (~2-3 min per image). GPU recommended!*
""")

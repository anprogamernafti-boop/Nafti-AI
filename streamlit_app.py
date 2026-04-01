#!/usr/bin/env python3
"""Nafti AI - Free SDXL Image Generator"""

import streamlit as st
from datetime import datetime
from io import BytesIO

st.set_page_config(
    page_title="Nafti AI",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Nafti AI Image Generator")
st.markdown("Generate stunning images using Stable Diffusion XL - **100% Free**")
st.divider()

# Load pipeline only when needed
@st.cache_resource
def load_pipeline():
    """Lazy load SDXL"""
    import torch
    from diffusers import AutoPipelineForText2Image
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    pipeline = AutoPipelineForText2Image.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
        variant="fp16" if device == "cuda" else None
    )
    return pipeline.to(device)

# Main inputs
prompt = st.text_area(
    "What would you like to generate?",
    placeholder="e.g., 'A beautiful sunset over mountains, oil painting style'",
    height=80
)

# Advanced options
with st.expander("⚙️ Advanced Options"):
    col1, col2 = st.columns(2)
    with col1:
        width = st.slider("Width", 256, 1024, 512, step=64)
        height = st.slider("Height", 256, 1024, 512, step=64)
    with col2:
        num_steps = st.slider("Steps (quality vs speed)", 15, 50, 25)
        guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5)

# Generate
if st.button("✨ Generate Image", type="primary", use_container_width=True):
    if not prompt.strip():
        st.warning("Please enter a prompt")
    else:
        try:
            # Load model
            status = st.status("🔄 Loading model and generating...", expanded=True)
            
            with status:
                st.write("Loading SDXL (first time only)...")
                pipeline = load_pipeline()
                
                st.write("Generating image...")
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                
                image = pipeline(
                    prompt=prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_steps,
                    guidance_scale=guidance_scale
                ).images[0]
                
                status.update(label="✅ Done!", state="complete")
            
            # Display
            st.success("✅ Generated successfully!")
            st.image(image, use_column_width=True)
            
            # Download
            buf = BytesIO()
            image.save(buf, format="PNG")
            st.download_button(
                "📥 Download",
                buf.getvalue(),
                f"nafti_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "image/png",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Free image generation powered by Stable Diffusion XL on Hugging Face Spaces")
---
✨ **Nafti AI** - Free Image Generation Powered by Stable Diffusion XL

🔗 [GitHub](https://github.com) | 📧 Contact

*Generating on CPU? It will be slower (~2-3 min per image). GPU recommended!*
""")
#!/usr/bin/env python3
import streamlit as st

st.title("🎨 Nafti AI Image Generator")
st.write("App is running! Click button below to generate images.")

if st.button("✨ Generate Image"):
    try:
        st.info("Loading model (first time takes 2 min)...")
        
        import torch
        from diffusers import AutoPipelineForText2Image
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.write(f"Using: {device}")
        
        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
        )
        pipe = pipe.to(device)
        
        st.write("Generating image...")
        image = pipe("a beautiful sunset, oil painting").images[0]
        st.image(image)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
✨ **Nafti AI** - Free Image Generation Powered by Stable Diffusion XL

🔗 [GitHub](https://github.com) | 📧 Contact

*Generating on CPU? It will be slower (~2-3 min per image). GPU recommended!*
""")
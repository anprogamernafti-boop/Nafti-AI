# 🎨 Nafti AI - Deployment Guide for HuggingFace Spaces

## Quick Start: Deploy on HuggingFace Spaces (Free GPU!)

### Step 1: Create HuggingFace Account
1. Go to https://huggingface.co/join
2. Create a free account

### Step 2: Create a Space
1. Go to https://huggingface.co/spaces/create
2. **Name**: `nafti-ai-image-gen` (or your choice)
3. **License**: Select any (MIT recommended)
4. **Space SDK**: Select **Streamlit**
5. Click "Create Space"

### Step 3: Upload Files
Clone or upload these files to your Space:
```
nafti-ai/
├── app.py                      # Main Streamlit app
├── requirements-hf-spaces.txt  # Python dependencies
└── .gitignore                  # Git ignore file
```

The Space will automatically:
- ✅ Install dependencies from `requirements.txt`
- ✅ Run `streamlit run app.py`
- ✅ Assign a free GPU T4 (if available)

### Step 4: Access Your App
Once deployed, your Space will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/nafti-ai-image-gen
```

---

## 🚀 Features

✨ **100% Free** - No credit card needed
⚡ **GPU Powered** - Free T4 GPU on HuggingFace Spaces
🎨 **Stable Diffusion XL** - State-of-the-art image generation
💾 **Download Images** - Save your creations as PNG
⚙️ **Advanced Options** - Control size, steps, and guidance

---

## ⏱️ Performance

| Hardware | Time per Image |
|----------|----------------|
| **GPU T4 (Spaces)** | ~60-90 seconds |
| **CPU** | ~3-5 minutes |

First generation is slower (~2-3 min) due to model loading.

---

## 🔧 Local Development

### Prerequisites
```bash
Python 3.10+
CUDA 11.8+ (optional, for faster GPU)
```

### Installation
```bash
# Clone or download the repository
cd nafti-ai

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements-hf-spaces.txt

# Run locally
streamlit run app.py
```

Then open: http://localhost:8501

---

## 📝 Notes

- **First Run**: Model downloads ~6GB on first generation (one-time)
- **Private Space**: Your Space is public by default. Set to private in Settings if needed
- **Persistent Storage**: Spaces have temporary storage. Generated images disappear after session ends
- **Rate Limiting**: HF Spaces has fair use policy (~30 generations/hour per user)

---

## 🆘 Troubleshooting

**Issue**: "CUDA out of memory"
- **Solution**: Reduce image size or steps in Advanced Options

**Issue**: "Model download failed"
- **Solution**: Check internet connection, retry. Model caches after first run

**Issue**: "Streamlit connection timeout"
- **Solution**: Normal for first load. Wait 2-3 minutes for model to download

---

## 📚 Resources

- [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Streamlit Docs](https://docs.streamlit.io)
- [Diffusers Library](https://huggingface.co/docs/diffusers)
- [Stable Diffusion XL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)

---

## 🎯 Next Steps

1. **Deploy**: Follow Step 1-4 above
2. **Share**: Share your Space link with friends!
3. **Customize**: Modify `app.py` to add features
4. **Monitor**: Check HuggingFace dashboard for usage stats

---

**Enjoy creating stunning AI images for free! 🎨✨**

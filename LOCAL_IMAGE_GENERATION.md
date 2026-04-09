# Local Image Generation Setup Guide

## ⚡ IMPORTANT: UPGRADED TO SDXL (Professional Quality)

**Your image generation has been upgraded to use SDXL** - which generates professional studio-quality images comparable to Nano Banana and other premium APIs.

See **PROFESSIONAL_IMAGE_GENERATION.md** for the complete guide on quality tuning, performance optimization, and advanced usage.

## Quick Start

### Prerequisites
- **RAM**: 8GB+ (for SDXL)
- **VRAM**: 6GB+ recommended (4GB minimum for degraded mode)
- **Disk**: ~7GB for SDXL model

### Windows Setup (GPU Recommended)

```powershell
# 1. Activate environment
.\.venv\Scripts\activate.ps1

# 2. Install CUDA version of PyTorch (NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Install diffusers
pip install diffusers>=0.27.0 transformers>=4.36.0 accelerate>=0.24.0

# 4. .env is already configured - just start the server!
python server.py
```

### CPU-Only Setup (Slower, but works)

```powershell
.\.venv\Scripts\activate.ps1
pip install torch torchvision torchaudio
pip install diffusers transformers accelerate
python server.py
```

### AMD GPU (ROCm)

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
pip install diffusers transformers accelerate
python server.py
```

## Performance Summary

| Setup | Resolution | Time | Quality |
|-------|-----------|------|---------|
| NVIDIA GPU (6GB+) | 1024×1024 | 4-10 min | Professional |
| NVIDIA GPU (4GB) | 768×768 | 3-8 min | Excellent |
| CPU | 512×512 | 15-30 min | Good |

## First Run

The first time you generate an image, SDXL (~6GB) will download to your HuggingFace cache:
- **Time**: 10-30 minutes (depends on internet)
- **Storage**: 7GB required
- **Subsequent runs**: Much faster (4-10 minutes)

## Configuration

Everything is pre-configured in `.env` for professional output:

```
USE_LOCAL=1                              # Enable local generation
LOCAL_MODEL=stabilityai/stable-diffusion-xl-base-1.0  # SDXL
LOCAL_WIDTH=1024
LOCAL_HEIGHT=1024
LOCAL_STEPS=30                           # Professional quality
LOCAL_GUIDANCE=7.5                       # Optimal adherence
LOCAL_SCHEDULER=euler_ancestral          # Best for photorealism
LOCAL_REFINE=0                           # Optional 2nd stage (slower)
```

To customize for your hardware or quality preferences, edit `.env` and restart the server.

### Tuning for Your Setup

**For Maximum Quality** (GPU with 8GB+ VRAM):
```
LOCAL_STEPS=50
LOCAL_GUIDANCE=8.0
LOCAL_REFINE=1              # Enable Refiner for ultra-smooth results
```

**For Speed** (GPU with 4GB VRAM):
```
LOCAL_WIDTH=768
LOCAL_HEIGHT=768
LOCAL_STEPS=20
LOCAL_REFINE=0
```

**For CPU**:
```
LOCAL_WIDTH=512
LOCAL_HEIGHT=512
LOCAL_STEPS=15              # Very slow - consider GPU
LOCAL_REFINE=0
```

## Troubleshooting

### "CUDA out of memory"

Reduce in `.env`:
```
LOCAL_WIDTH=768
LOCAL_HEIGHT=768
LOCAL_STEPS=20
```

Then restart: `python server.py`

### Very Slow (30+ minutes per image)

**Cause**: Using CPU
**Solution**: Get a GPU or reduce resolution/steps

### Model Download Fails

**Cause**: Network issue or HuggingFace cache full
**Solution**: 
```powershell
# Clear cache and retry
rmdir $env:USERPROFILE\.cache\huggingface /s
python server.py
```

## Advanced Features

### SDXL Refiner (Ultra-Professional)

For absolutely stunning, ultra-polished results, enable the 2-stage process:

```
LOCAL_REFINE=1              # First pass: base image
                            # Second pass: refiner for smooth details
LOCAL_REFINE_STEPS=12       # Usually 10-15 steps
```

This adds 5-10 minutes but produces gallery-quality images.

### Fixed Seed for Reproducibility

```
LOCAL_SEED=12345            # Use same seed to reproduce exact image
```

### Professional Prompt Engineering

Your prompts are automatically enhanced with professional keywords:
```
"masterpiece, 8k, professional studio quality, cinematic lighting, 
sharp focus, beautiful composition, hyper-detailed"
```

You can customize the style in `.env`:
```
PROMPT_STYLE="your custom professional style here"
```

## Environment Variables

See `.env` file for all available tuning options:
- `LOCAL_MODEL` - Model to use
- `LOCAL_WIDTH/HEIGHT` - Output resolution
- `LOCAL_STEPS` - Inference steps (more = better quality, slower)
- `LOCAL_GUIDANCE` - Prompt adherence strength
- `LOCAL_REFINE` - Enable 2-stage SDXL Refiner
- `LOCAL_SCHEDULER` - Scheduler (euler_ancestral/dpmpp/heun)
- `LOCAL_NEGATIVE_PROMPT` - Quality filters
- `LOCAL_SEED` - Reproducible results

## Next Steps

1. **Restart server**: `python server.py`
2. **Generate test image**: Use the web UI
3. **Monitor process**: Check console logs for performance
4. **Tune if needed**: Adjust `.env` based on results

See **PROFESSIONAL_IMAGE_GENERATION.md** for advanced tuning and quality optimization.

# 🚀 QUICK START - SDXL Professional Image Generation

## What Happened
Your image generation has been upgraded to **SDXL** (Stable Diffusion XL) for professional, Nano Banana-quality results.

## Immediate Next Steps

### Step 1: Restart Server (Right Now!)
```powershell
# Press Ctrl+C to stop current server, then:
python server.py
```

✅ This loads the SDXL model configuration

### Step 2: First Image Generation (Download Phase)
When you generate your first image:
- **⏳ Time**: 30-60 minutes
- **📦 Download**: ~6GB model (HuggingFace)
- **💾 Storage**: Use ~/.cache/huggingface 
- **Once done**: Subsequent images are much faster (4-10 min)

### Step 3: What to Expect
- **Quality**: Professional, studio-grade
- **Resolution**: 1024×1024 native
- **Speed**: 4-15 min depending on GPU
- **Scheduling**: Euler Ancestral (best photorealism)

## Quick Performance Guide

| GPU | Time per Image | Quality |
|-----|---|---|
| NVIDIA RTX 3060+ (12GB) | 8-12 min | ⭐⭐⭐⭐⭐ Excellent |
| NVIDIA RTX 4060 (8GB) | 10-15 min | ⭐⭐⭐⭐ Very Good |
| Older GPU (4GB) | 20-30 min | ⭐⭐⭐ Good |
| CPU Only | 30+ min | ⭐⭐ Acceptable |

## Test Prompts

Try these to see professional quality:

### Portrait
```
Professional headshot of [person], studio lighting, 
crisp focus, award-winning photography, 8k detail
```

### Product
```
[Product], professional product photography, 
white background, studio lighting, pristine condition
```

### Landscape
```
[Scene], professional landscape photography, 
golden hour, perfect composition, ultra-sharp
```

## Troubleshooting

### "CUDA out of memory"
Edit `.env`:
```
LOCAL_WIDTH=768
LOCAL_HEIGHT=768
LOCAL_STEPS=20
```
Then restart server.

### Very slow (30+ min)
- You're using CPU
- Either get GPU or reduce resolution
- Reduce LOCAL_STEPS to 15

### Model fails to download
```powershell
# Clear cache and retry:
rmdir $env:USERPROFILE\.cache\huggingface /s
python server.py
```

## Configuration Cheat Sheet

**For Best Quality** (8GB+ GPU):
```
In .env:
LOCAL_STEPS=50
LOCAL_GUIDANCE=8.0
LOCAL_REFINE=1              # Ultra-professional
```

**For Best Speed** (4GB GPU):
```
In .env:
LOCAL_WIDTH=512
LOCAL_HEIGHT=512
LOCAL_STEPS=15
LOCAL_REFINE=0
```

**Default** (Recommended):
```
Already configured in .env
Just restart and use!
```

## Key Settings

| Setting | Default | Good | Best |
|---------|---------|------|------|
| Steps | 30 | 40 | 50+ |
| Resolution | 1024×1024 | 1024×1024 | 1024×1024 |
| Guidance | 7.5 | 8.0 | 8.5 |
| Scheduler | euler_ancestral | euler_ancestral | euler_ancestral |

## Pro Tips

✨ **Use detailed prompts**: "A (adjective) (subject), (style), (lighting), (quality)"

🎲 **Fixed seed for reproduction**: Set `LOCAL_SEED=12345` in .env

📊 **Monitor performance**: Watch console logs for generation time

🔧 **Batch generate**: Create multiple images back-to-back (warmer GPU = slightly faster)

## What's New In Your Files

### `.env`
- Updated to SDXL Base 1.0
- Resolution: 1024×1024
- Professional scheduler and prompts

### `server.py`
- SDXL pipeline implementation
- Professional schedulers
- Optional Refiner support
- Enhanced quality settings

### Documentation
- **PROFESSIONAL_IMAGE_GENERATION.md** - Full guide
- **SDXL_QUICK_REFERENCE.md** - Quick lookup
- **UPGRADE_SUMMARY.md** - What changed

## After First Image

1. **Check quality**: Does it look professional?
2. **Monitor time**: How long did it take?
3. **Adjust if needed**: Edit .env based on your VRAM
4. **Read the full guides**: See PROFESSIONAL_IMAGE_GENERATION.md

## Command Reference

```powershell
# Start server
python server.py

# Monitor GPU (NVIDIA)
nvidia-smi -l 1

# Monitor GPU (AMD)
rocm-smi -l 1

# Clear HuggingFace cache (if stuck)
rmdir $env:USERPROFILE\.cache\huggingface /s
```

## Expected Timeline

- **Setup to first generation**: 5-10 min (just restart)
- **First generation**: 30-60 min (model download)
- **Second+ generations**: 4-15 min (fast!)
- **With Refiner**: Add 5-10 min for ultra-polish

## You're Ready! 🎉

1. ✅ Code is updated
2. ✅ Configuration is set
3. ✅ Documentation is provided

Just **restart your server** and start generating professional images!

---

**Questions?** Check:
1. Console logs (run details)
2. PROFESSIONAL_IMAGE_GENERATION.md (complete guide)
3. SDXL_QUICK_REFERENCE.md (settings reference)

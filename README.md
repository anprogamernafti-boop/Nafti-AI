# Nafti AI Web App

This repository contains the Nafti AI progressive web application with an integrated
email/password and Google authentication layer. The core chat functionality is
unchanged, and authentication simply guards access to the interface.

## Features

- Chat interface powered by Groq API (`/api/ai` proxy)
- **Image generation** with intelligent fallback chain (prioritizes reliability):
  1. **Replicate** ⭐ — free, stable, professional (RECOMMENDED)
  2. Gemini (Google) — if API key configured
  3. Pollinations.ai — free but unreliable
- Multi-session support with per-user conversation storage
  - Start new sessions or clear current session from the header
  - View all sessions on a dedicated history page (with delete option)
- PWA support with service worker & install prompts
- Splash intro screen on each visit
- Theme toggle (light/dark)
- **Authentication**:
  - Email / password (stored in flat files)
  - Google OAuth2 (via `flask-dance`)


## Setup

1. **Use a 64‑bit Python interpreter**
   - PyTorch (required for local image generation) is only available for 64‑bit Python. Confirm your installation with:
     ```powershell
     python -c "import platform, sys; print(platform.architecture(), sys.maxsize>2**32)"
     ```
     The output should show `('64bit', ...)` or `True`.
   - If you have a 32‑bit Python, download and install the **64‑bit installer** from https://www.python.org/downloads/windows/.
   - After installing 64‑bit Python, recreate the virtual environment:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     pip install -r requirements.txt
     ```
   - Continue with the rest of the setup below.


2. **Configure environment** in `.env`:

   ```dotenv
   GROQ_API_KEY=your_groq_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
   SECRET_KEY=some_random_secret
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   
   # Image generation services (all free, all optional)
   # For best results, set up Replicate (free, professional, stable)
   REPLICATE_API_TOKEN=your_replicate_token_from_https://replicate.com/account/api-tokens
   REPLICATE_MODEL=black-forest-labs/flux-pro   # or stabilityai/stable-diffusion-xl
   
   # Gemini (Google) — optional, leave blank to skip
   GEMINI_API_KEY=your_google_gemini_key
   GEMINI_IMAGE_MODEL=gemini-2.5-flash-image
   
   # Pollinations.ai — final fallback (free but unreliable)
   USE_POLLINATIONS=1
   
   # Local Stable Diffusion options (enable with USE_LOCAL=1):
   # The pipeline defaults to a lightweight 512×512 v1.5 model but you can
   # improve quality by increasing resolution/steps or using a different
   # model (e.g. stabilityai/stable-diffusion-2-1 or an SDXL variant).
   #
   #   LOCAL_MODEL=runwayml/stable-diffusion-v1-5
   #   LOCAL_WIDTH=768            # 1024×1024 will need a decent GPU
   #   LOCAL_HEIGHT=768
   #   LOCAL_STEPS=50              # more steps -> better detail, slower
   #   LOCAL_GUIDANCE=8.0          # 7.5 is fine, 8–9 pushes style harder
   #   LOCAL_FP16=true             # enables fp16 on CUDA device
   #   USE_LOCAL=1                 # turn on the local pipeline
   #
   # Prompt-engineering helpers (optional) – a short phrase prepended to
   #   every prompt to encourage high‑quality output.  Examples:
   #
   #   PROMPT_STYLE="highly detailed, professional quality, studio lighting"
   #   PROMPT_DISABLE=1    # set true to ignore PROMPT_STYLE entirely
   #
   # Local generator extras
   #
   #   LOCAL_NEGATIVE_PROMPT="blurry, low quality, watermark"
   #   LOCAL_SEED=12345         # set for reproducible results
   #   LOCAL_SCHEDULER=euler    # [euler|ddim|dpmsolver|lms] choose sampling algorithm
   #   LOCAL_UPSCALE=1          # simple Lanczos resize after generation
   #   LOCAL_UPSCALE_FACTOR=2   # multiplier for upscaling
   #
   # The code also applies a heuristic to increase `LOCAL_STEPS` when you
   # generate at resolutions above 512×512 or 768×768, so you don't need to
   # manually bump it in most cases.
   ```

   **Image Generation Pipeline (in order of priority):**
   1. **Replicate** ⭐ — Recommended! Free account, stable, professional results
   2. Gemini — if API key configured
   3. Pollinations.ai — unreliable fallback

   - Google credentials are obtained from the Google Cloud Console under OAuth2.
   - If you don't need Google login, you may leave those empty; email/password still works.

3. **Run the server**:
   ```powershell
   python server.py
   ```

- User & chat data files (`users.json`, `history.json`) will be created automatically on first run.

4. **Open** http://localhost:5000 in your browser. You will see the login/registration page.

## Notes

- Remember to keep `.env` out of version control (already listed in `.gitignore`).
- The original `index.html` at workspace root is no longer used; the template in
  `templates/index.html` is rendered by Flask.
- The `/api/ai` route still proxies to Groq exactly as before; no changes were made.

## Extending

If you later wish to add features (password reset, email verification, user profiles,
etc.) you can modify `server.py` and the global template accordingly. The authentication
mechanism is standard Flask-Login + SQLAlchemy and should be straightforward.

Enjoy building with Nafti AI! 🚀
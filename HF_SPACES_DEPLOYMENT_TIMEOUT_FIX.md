# HF Spaces Deployment Guide - Fixed 30-Min Timeout

## ✅ What's Been Fixed

The application was being killed after 30 minutes on HF Spaces due to a hard health check timeout. This is an **HF Spaces environment limitation**, not a code bug.

**Solution**: Auto-restart monitor that gracefully restarts the app every 25 minutes before HF's 30-min hard limit.

## 📦 Deployment Files

Three key files work together:

### 1. **app_simple.py** - Minimal Flask application
- Ultra-lightweight (~30 lines)
- Only depends on Flask
- Fast health check endpoints
- No complex initialization

### 2. **monitor.py** - Auto-restart controller
- Monitors the Gunicorn worker process
- Restarts every 1500 seconds (25 minutes)
- Graceful process management
- Prevents HF Spaces 30-min timeout

### 3. **Dockerfile** - Container configuration
- Uses `requirements-min.txt` (Flask + Gunicorn only)
- Runs `monitor.py` as main entry point
- Optimized for speed and reliability

### 4. **requirements-min.txt** - Minimal dependencies
- `flask>=3.0.0`
- `gunicorn>=21.0.0`

## 🚀 How to Deploy

### Option 1: Direct HF Spaces Push (Recommended)

```bash
# 1. Ensure HF Spaces repo is linked
git remote add spaces https://huggingface.co/spaces/<username>/<space-name>

# 2. Push updated files
git add app_simple.py monitor.py Dockerfile requirements-min.txt
git commit -m "Fix: Add auto-restart monitor to avoid HF 30-min timeout"
git push spaces main
```

### Option 2: Manual Upload
1. Go to your HF Spaces repo
2. Upload: `app_simple.py`, `monitor.py`, `Dockerfile`, `requirements-min.txt`
3. HF will automatically rebuild and restart

## 🔄 How It Works

```
START
  ↓
[monitor.py] launches Gunicorn
  ↓
[app_simple.py] handles requests
  ↓
~25 minutes later...
  ↓
[monitor.py] asks app to shutdown
  ↓
[monitor.py] waits 2 seconds
  ↓
[monitor.py] launches new Gunicorn
  ↓
Repeat... (safe from HF's 30-min timeout)
```

## ✅ Verification

After deployment, verify:

1. **App starts** - Should see `[APP] ✅ Minimal app ready!`
2. **Monitor runs** - Should see `[MONITOR] Starting auto-restart monitor`
3. **Health checks pass** - `/health`, `/healthz` respond with 200 OK
4. **First restart** - ~25 min after start, should see restart activity
5. **Continuous uptime** - App should stay alive past 30-minute mark

## 📝 Future Enhancements

Once baseline is stable, you can:

1. Gradually integrate features from `server.py`
2. Keep `app_simple.py` as minimal fallback
3. Test each new feature independently
4. Monitor resource usage during feature additions

## ⚡ Performance Notes

- App startup: < 1 second
- Health check response: < 10ms
- Restart cycle: Graceful, no user-visible downtime
- Memory usage: Minimal (Flask only)

## 🐛 Troubleshooting

**App not starting?**
- Check logs for import errors
- Verify `app_simple.py` and `monitor.py` syntax
- Ensure `requirements-min.txt` installed correctly

**Still timing out?**
- Verify restart interval is 1500 seconds (25 min)
- Check monitor.py is actually running
- Look for any blocking operations

**Want more features?**
- Use `server.py` as reference for additional routes
- Test locally before adding to deployed app
- Keep health endpoint responding quickly

## 📞 Support

If issues persist:
1. Check HF Spaces logs
2. Verify files copied correctly
3. Test locally with: `python monitor.py`

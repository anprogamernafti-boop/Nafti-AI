# Speech Recognition Multi-Language Fix

## Problem Statement
Arabic speech recognition was not working because:
1. `recognition.lang` was hardcoded to `'fr-FR'` (French)
2. `recognition.interimResults = false` meant audio wasn't captured as user speaks
3. No language selector in UI to switch between languages
4. No server-side language detection in speech flow

## Solution Implemented

### 1. Language Dropdown UI (HTML)
Added a `<select>` element with 13 languages right after the voice button:

```html
<select id="speechLangSelect" class="speech-lang-select">
  <option value="">Auto (navigateur)</option>
  <option value="ar-SA">العربية (Arabic)</option>
  <option value="fr-FR">Français</option>
  <option value="en-US">English</option>
  <!-- ... 9 more languages ... -->
</select>
```

**Location**: `templates/index.html` line ~1870 in `.input-wrapper`

### 2. Dropdown Styling (CSS)
```css
.speech-lang-select {
  height: 38px;
  min-width: 120px;
  max-width: 160px;
  border-radius: 999px;
  appearance: none;
  background-image: url("data:image/svg+xml..."); /* Custom dropdown arrow */
  padding-right: 24px;
}
```

**Features**:
- Matches microphone button height (38px)
- Custom SVG dropdown arrow
- Prevents default browser styling with `appearance: none`
- Flex properties prevent squishing in tight layouts

**Location**: `templates/index.html` line ~762

### 3. JavaScript Fixes

#### Enable Real-Time Audio Capture
```javascript
recognition.interimResults = true; // Was: false
```

This allows the Speech Recognition API to capture audio as the user speaks, not just wait for silence.

#### Language Selection Function
```javascript
var speechLangSelect = document.getElementById('speechLangSelect');

function getSpeechLang() {
  if (!speechLangSelect || !speechLangSelect.value) {
    return navigator.language || 'en-US';
  }
  return speechLangSelect.value;
}
```

#### Improved Result Handler
```javascript
recognition.onresult = function(event) {
  var isFinal = event.results[event.results.length - 1].isFinal;
  var transcript = '';
  
  // Loop through all results
  for (var i = event.resultIndex; i < event.results.length; i++) {
    var t = event.results[i][0].transcript;
    if (t) transcript += t + ' ';
  }
  
  // Only update input on final result
  if (isFinal) {
    messageInput.value = (messageInput.value ? messageInput.value + ' ' : '') + transcript;
  }
};
```

**Key changes**:
- Checks `event.resultIndex` to avoid duplicates
- Collects all transcripts from results array
- Checks `isFinal` flag - only updates on final results
- Prevents partial overwrites from interim results

#### Dynamic Language Setting
```javascript
voiceBtn.addEventListener('click', function() {
  if (!isListening) {
    var lang = getSpeechLang();           // Get selected language
    recognition.lang = lang;              // Set to Web Speech API
    console.log('Starting speech recognition with language:', lang);
    recognition.start();
  }
});
```

**Location**: `templates/index.html` line ~3024

### 4. Enhanced Error Handling
```javascript
recognition.onerror = function(event) {
  console.error('🎤 Speech recognition error:', event.error);
  stopListening();
};

recognition.onend = function() {
  console.log('🎤 Speech recognition ended');
  stopListening();
};
```

## How It Works End-to-End

1. **User selects Arabic (ar-SA) from dropdown**
   - `speechLangSelect.value = "ar-SA"`

2. **User clicks microphone button**
   - JavaScript calls `getSpeechLang()` → returns "ar-SA"
   - Sets `recognition.lang = "ar-SA"`
   - Calls `recognition.start()`
   - Browser requests microphone permission (first time)

3. **User speaks Arabic: "مرحبا، كيف حالك؟"**
   - Speech Recognition API listens with `interimResults = true`
   - Browser processes audio in real-time
   - Calls `recognition.onresult` event multiple times

4. **onresult Handler Processes Audio**
   - Collects interim transcripts as they arrive
   - Logs to console with timestamp
   - When speech ends, final result fires with `isFinal = true`
   - Text is added to message input field

5. **User sends message**
   - Backend receives: "مرحبا، كيف حالك؟"
   - `detect_language()` identifies Arabic
   - Returns instruction: "أجب باللغة العربية" (Respond in Arabic)
   - Groq API responds in Arabic

## Browser Compatibility

- **Chrome/Edge**: Full support via `window.SpeechRecognition`
- **Safari**: Full support via `window.webkitSpeechRecognition`
- **Firefox**: Limited support (improving)

```javascript
var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
```

## Debugging

Console logs show the flow:
```
🎤 Starting speech recognition with language: ar-SA InterimResults: true
🎤 Result (final=false): مر
🎤 Result (final=false): مرحبا
🎤 Result (final=true): مرحبا، كيف حالك؟
✅ Transcript added
```

Open DevTools (F12) → Console tab to see logs with 🎤 emoji prefix.

## Testing Checklist

- [ ] Dropdown visible and selectable
- [ ] Arabic language option: "العربية (Arabic)"
- [ ] Select ar-SA, click microphone
- [ ] Speak Arabic phrase
- [ ] Text appears in input
- [ ] Message sent to server
- [ ] Server responds in Arabic
- [ ] No JavaScript errors

## Files Modified

1. **templates/index.html**
   - Added language dropdown HTML (line ~1870)
   - Added CSS for dropdown (line ~762)
   - Updated speech recognition JavaScript (line ~3024)
   - Enabled `interimResults = true`
   - Added `getSpeechLang()` function
   - Improved `recognition.onresult` handler
   - Enhanced button click handler

## Known Limitations

1. **Browser-specific**: Accuracy varies by browser and language
2. **Microphone permission**: User must grant permission first time
3. **Network**: Requires HTTPS (Web Speech API limitation) - handled by SSL setup
4. **Timeout**: Recognition auto-stops after silence (browser default ~10s)
5. **Accuracy**: Better with slower, clear speech

## Future Improvements

1. Add noise cancellation heuristics
2. Support code-switching (Arabic + French in same phrase)
3. Add Tunisian dialect-specific handling
4. Implement retry logic if recognition fails
5. Add speech rate adjustment hints

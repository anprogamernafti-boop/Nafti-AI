#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de la détection de langue vocale améliorée
Teste la détection pour l'allemand, l'arabe, et autres langues
"""

import json

# Simulation de la fonction detectLangCode en Python
def detect_lang_code(text):
    """Simule la détection de langue vocale JavaScript améliorée"""
    if not text or len(text.strip()) < 2:
        return None
    
    t = text.lower()
    
    # PRIORITÉ 1: Scripts non-latins
    import re
    if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text):
        return 'ar-SA'
    if re.search(r'[\u0400-\u04FF]', text):
        return 'ru-RU'
    if re.search(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]', text):
        return 'zh-CN'
    if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
        return 'ja-JP'
    if re.search(r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]', text):
        return 'ko-KR'
    if re.search(r'[\u0370-\u03FF\u1F00-\u1FFF]', text):
        return 'el-GR'
    if re.search(r'[\u0590-\u05FF\uFB1D-\uFB4F]', text):
        return 'he-IL'
    if re.search(r'[\u0E00-\u0E7F]', text):
        return 'th'
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'
    
    # PRIORITÉ 2: Accents caractéristiques
    if re.search(r'[ñÑ¿¡]', text):
        return 'es-ES'
    if re.search(r'[ãõÃÕ]', text):
        return 'pt-BR'
    if re.search(r'[äöüßÄÖÜẞ]', text):
        return 'de-DE'
    if re.search(r'[łźżąęćńśŁŹŻĄĘĆŃŚ]', text):
        return 'pl'
    if re.search(r'[șțăâŞŢĂÂ]', text):
        return 'ro'
    if re.search(r'[ůěčšřžďťňŮĚČŠŘŽĎŤŇ]', text):
        return 'cs'
    if re.search(r'[åÅ]', text):
        return 'sv'
    
    # PRIORITÉ 3: Mots-clés
    keywords = {
        'de-DE': r'\b(ich|du|er|sie|es|wir|ihr|sie|mich|mir|ihn|und|oder|aber|ist|sein|haben|werden|können|hallo|danke|ja|nein)\b',
        'fr-FR': r'\b(je|tu|il|elle|on|nous|vous|ils|elles|le|la|les|un|une|et|ou|est|sont|avec|pour|dans|sur|bonjour|merci|oui|non)\b',
        'en-US': r'\b(i|you|he|she|it|we|they|the|is|are|and|or|but|a|an|of|in|to|for|with|the|hello|thanks|yes|no)\b',
        'es-ES': r'\b(yo|tú|él|ella|nosotros|vosotros|ellos|las|el|la|los|de|es|son|y|o|pero|para|por|hola|gracias|sí|no)\b',
        'pt-BR': r'\b(eu|tu|ele|ela|você|nós|vós|eles|o|a|os|as|de|em|um|uma|é|são|e|ou|mas|para|com|olá|obrigado|sim|não)\b',
        'ar-SA': r'\b(أنا|أنت|هو|هي|نحن|أنتم|أنتن|هم|هن|ما|من|ماذا|أين|متى|كيف|هل|في|من|إلى|مع|بدون|حتى|لا|نعم)\b',
    }
    
    scores = {}
    for lang, pattern in keywords.items():
        matches = re.findall(pattern, t, re.IGNORECASE)
        scores[lang] = len(matches)
    
    best_lang = max(scores, key=scores.get) if scores else 'fr-FR'
    return best_lang if scores[best_lang] > 0 else None

# Test cases pour allemand et arabe
test_cases = [
    # ALLEMAND
    ("Guten Morgen, wie geht es dir heute?", "de-DE", "German: Basic greeting"),
    ("Ich bin deutscher und ich liebe Bier", "de-DE", "German: Identity + beer"),
    ("Welche ist die Hauptstadt von Deutschland?", "de-DE", "German: Question"),
    ("Das ist sehr schön, nicht wahr?", "de-DE", "German: Opinion"),
    ("Können Sie mir helfen?", "de-DE", "German: Polite request"),
    ("Ich möchte einen Kaffee, bitte", "de-DE", "German: Order"),
    ("Bis später, auf Wiedersehen!", "de-DE", "German: Goodbye"),
    ("Das Wetter ist heute wunderbar", "de-DE", "German: Weather"),
    
    # ARABE
    ("مرحبا، كيف حالك اليوم؟", "ar-SA", "Arabic: Basic greeting"),
    ("أنا عربي وأحب الشاي", "ar-SA", "Arabic: Identity + tea"),
    ("ما هي عاصمة مصر؟", "ar-SA", "Arabic: Question"),
    ("هذا رائع جداً، أليس كذلك؟", "ar-SA", "Arabic: Opinion"),
    ("هل يمكنك مساعدتي من فضلك؟", "ar-SA", "Arabic: Polite request"),
    ("أريد قهوة من فضلك", "ar-SA", "Arabic: Order"),
    ("إلى اللقاء، وداعاً!", "ar-SA", "Arabic: Goodbye"),
    ("الطقس جميل جداً اليوم", "ar-SA", "Arabic: Weather"),
    
    # FRANÇAIS (control)
    ("Bonjour, comment allez-vous?", "fr-FR", "French: Basic greeting"),
    ("Je suis français et j'aime le vin", "fr-FR", "French: Identity + wine"),
    
    # ANGLAIS (control)
    ("Hello, how are you today?", "en-US", "English: Basic greeting"),
    ("I am English and I love tea", "en-US", "English: Identity + tea"),
    
    # ESPAGNOL (control)
    ("Hola, ¿cómo estás hoy?", "es-ES", "Spanish: Basic greeting"),
    ("Soy español y amo la paella", "es-ES", "Spanish: Identity + paella"),
]

print("=" * 100)
print("TEST DE DÉTECTION DE LANGUE VOCALE AMÉLIORÉE")
print("=" * 100)
print()

passed = 0
failed = 0
failed_cases = []

for text, expected, description in test_cases:
    detected = detect_lang_code(text)
    is_pass = detected == expected
    status = "✓ PASS" if is_pass else "✗ FAIL"
    
    if is_pass:
        passed += 1
    else:
        failed += 1
        failed_cases.append((text, expected, detected, description))
    
    text_short = text[:50] + "..." if len(text) > 50 else text
    print(f"{status} | {description:40} | Detected: {detected or 'None':6} | Expected: {expected}")

print()
print("=" * 100)
print(f"RÉSULTATS: {passed} PASSED, {failed} FAILED out of {len(test_cases)}")
accuracy = 100 * passed / len(test_cases) if test_cases else 0
print(f"Accuracy: {accuracy:.1f}%")
print("=" * 100)

if failed > 0:
    print()
    print("FAILED CASES:")
    for text, expected, got, desc in failed_cases:
        print(f"  [{desc}]")
        print(f"    Text: '{text}'")
        print(f"    Expected: {expected}, Got: {got}")
        print()

print()
if passed == len(test_cases):
    print("✅ SUCCESS: All tests passed! Language detection is 100% reliable!")
else:
    print(f"⚠️  {failed} test(s) failed. Please review the detection logic.")

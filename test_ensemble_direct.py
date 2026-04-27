#!/usr/bin/env python3
"""
🧠 DIRECT TEST - Tester les fonctions d'ensemble DIRECTEMENT sans API
"""

import sys
sys.path.insert(0, '/Users/Asser/Desktop/nafti-ai')

# Importer les fonctions directement depuis server.py
from server import detect_language_ensemble, detect_language

# Test data
TEST_DATA = {
    "ar": [
        "مرحبا، كيف حالك؟ أتمنى أن تكون بخير!",
        "السلام عليكم ورحمة الله وبركاته",
    ],
    "de": [
        "Guten Morgen! Wie geht es dir heute?",
        "Ich bin ein Programmierer und ich arbeite mit Python.",
    ],
    "fr": [
        "Bonjour, comment allez-vous aujourd'hui?",
        "Je m'appelle Pierre et je suis français de Paris.",
    ],
    "en": [
        "Hello, how are you doing today?",
        "I am a software engineer working with Python.",
    ],
}

print("🧠 TEST DIRECT - Détection de Langue INTELLIGENTE ENSEMBLE")
print("=" * 70)

results = {}

for target_lang, texts in TEST_DATA.items():
    print(f"\n🇪 {target_lang.upper()}:")
    results[target_lang] = {"passed": 0, "total": 0}
    
    for text in texts:
        results[target_lang]["total"] += 1
        
        try:
            # Test the ensemble function
            result = detect_language_ensemble(text)
            detected_lang = result.get("language")
            confidence = result.get("confidence", 0)
            method = result.get("method", "unknown")
            
            is_correct = detected_lang == target_lang
            emoji = "✅" if is_correct else "❌"
            
            print(f"  {emoji} {detected_lang.upper()} (conf: {confidence:.2f}, {method})")
            print(f"     Text: {text[:60]}...")
            
            if is_correct:
                results[target_lang]["passed"] += 1
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

# Summary
print("\n" + "=" * 70)
print("\n📊 RÉSUMÉ DES RÉSULTATS:\n")

total_passed = 0
total_tests = 0

for lang in sorted(TEST_DATA.keys()):
    stats = results[lang]
    passed = stats["passed"]
    total = stats["total"]
    percentage = (passed / total * 100) if total > 0 else 0
    total_passed += passed
    total_tests += total
    
    status_emoji = "✅" if percentage == 100 else "⚠️ " if percentage >= 50 else "❌"
    print(f"  {status_emoji} {lang.upper()}: {passed}/{total} ({percentage:.0f}%)")

print(f"\n  📈 TOTAL: {total_passed}/{total_tests} ({total_passed/total_tests*100:.0f}%)")

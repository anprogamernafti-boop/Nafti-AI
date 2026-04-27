#!/usr/bin/env python3
"""
🧠 TEST SUITE - Détection de Langue INTELLIGENTE ENSEMBLE
─────────────────────────────────────────────────────────

Test de la nouvelle détection NLP qui détecte TOUS les mots réels
et patterns linguistiques, pas seulement des mots-clés prédéfinis.
"""

import sys
import requests
import json
import urllib3

# Désactiver les avertissements SSL (certificat auto-signé)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Démarrer le serveur: python server.py

BASE_URL = "https://localhost:5000"  # HTTPS avec certificat auto-signé

# ── DONNÉES DE TEST ──────────────────────────────────────
TEST_DATA = {
    "ar": [
        "مرحبا، كيف حالك؟ أتمنى أن تكون بخير!",
        "السلام عليكم ورحمة الله وبركاته",
        "هذا نص عربي طويل يحتوي على كلمات متعددة من اللغة العربية",
        "شكراً لك كثيراً على ما فعلته من أجلي، أنت شخص رائع جداً",
    ],
    "de": [
        "Guten Morgen! Wie geht es dir heute?",
        "Ich bin ein Programmierer und ich arbeite mit Python und JavaScript.",
        "Äpfel, Öl, Überraschung, Glück - deutsche Wörter mit Umlauten",
        "Das ist ein längerer deutsche Text mit vielen Wörtern um zu testen",
    ],
    "fr": [
        "Bonjour, comment allez-vous aujourd'hui?",
        "Je m'appelle Pierre et je suis français de Paris.",
        "Les accents français: àâçèêëîïôùûüœæ sont très importants",
        "Ceci est un texte français assez long pour tester la détection intelligente",
    ],
    "en": [
        "Hello, how are you doing today?",
        "I am a software engineer working with Python and JavaScript languages.",
        "The English language is spoken by many people around the world.",
        "This is a longer English text with multiple sentences to test detection",
    ],
    "es": [
        "¡Hola! ¿Cómo estás hoy?",
        "Me llamo Juan y soy de España, de la ciudad de Madrid.",
        "Los acentos españoles: ñ, á, é, í, ó, ú son característicos",
        "Este es un texto español largo para probar la detección inteligente",
    ],
    "pt": [
        "Olá, como você está hoje?",
        "Meu nome é Carlos e sou programador brasileiro.",
        "Os acentos portugueses: ã, õ, á, é, í, ó, ú são importantes",
        "Este é um texto português longo para testar a detecção inteligente",
    ],
    "it": [
        "Ciao! Come stai oggi?",
        "Mi chiamo Marco e sono un programmatore italiano da Roma.",
        "Gli accenti italiani: à, è, é, ì, ò, ù caratterizzano la lingua",
        "Questo è un testo italiano abbastanza lungo per testare il rilevamento",
    ],
    "ru": [
        "Привет! Как дела?",
        "Меня зовут Иван и я русский программист.",
        "Русский язык использует кириллицу вместо латинского алфавита.",
        "Это длинный русский текст для проверки интеллектуального обнаружения языка",
    ],
}


def test_language_detection():
    """Tester l'endpoint de détection de langue"""
    print("🧠 TEST - Détection de Langue INTELLIGENTE ENSEMBLE\n")
    print("=" * 70)
    
    results = {lang: {"passed": 0, "total": 0, "details": []} for lang in TEST_DATA}
    
    for target_lang, texts in TEST_DATA.items():
        print(f"\n🇪 {target_lang.upper()}:")
        
        for text in texts:
            results[target_lang]["total"] += 1
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/detect-language",
                    json={"text": text},
                    timeout=5,
                    verify=False  # Ignorer la vérification SSL (certificat auto-signé)
                )
                
                if response.status_code != 200:
                    print(f"  ❌ HTTP {response.status_code}: {text[:40]}...")
                    results[target_lang]["details"].append({
                        "text": text[:40],
                        "status": "error",
                        "code": response.status_code
                    })
                    continue
                
                result = response.json()
                detected_lang = result.get("language")
                confidence = result.get("confidence", 0)
                method = result.get("method", "unknown")
                
                # Vérifier si la langue détectée est correcte
                is_correct = detected_lang == target_lang
                
                # Affichage
                emoji = "✅" if is_correct else "❌"
                print(f"  {emoji} {detected_lang.upper()} (conf: {confidence:.2f}, {method})")
                print(f"     Text: {text[:60]}...")
                
                if is_correct:
                    results[target_lang]["passed"] += 1
                
                results[target_lang]["details"].append({
                    "text": text[:40],
                    "detected": detected_lang,
                    "confidence": confidence,
                    "method": method,
                    "correct": is_correct
                })
                
            except requests.exceptions.ConnectionError:
                print(f"  ⚠️  Cannot connect to {BASE_URL}")
                print("  → Make sure server is running: python server.py")
                return
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                results[target_lang]["details"].append({
                    "text": text[:40],
                    "error": str(e)
                })
    
    # ── RÉSUMÉ ────────────────────────────────────────────
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
    
    # ── DÉTAILS ────────────────────────────────────────────
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        print("\n" + "=" * 70)
        print("\n📋 DÉTAILS COMPLETS:\n")
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_language_detection()

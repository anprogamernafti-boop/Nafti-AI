#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test complet de la détection de langue et des réponses multilingues.
Teste 0% d'erreur dans la détection et la réponse en même langue.
"""

import sys
import os

# Ajouter le répertoire du serveur au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import detect_language, get_language_instruction

# Test cases: (prompt, expected_language)
test_cases = [
    # Français
    ("Bonjour, comment ça va ?", "fr"),
    ("Je m'appelle Alice et je suis française", "fr"),
    ("Quelle est la capitale de la France ?", "fr"),
    ("J'aime les croissants et le café", "fr"),
    
    # Anglais
    ("Hello, how are you?", "en"),
    ("What is the capital of England?", "en"),
    ("I love coffee and tea", "en"),
    ("Can you help me with this?", "en"),
    
    # Espagnol
    ("Hola, ¿cómo estás?", "es"),
    ("¿Cuál es la capital de España?", "es"),
    ("Me encanta la paella", "es"),
    
    # Allemand
    ("Hallo, wie geht es dir?", "de"),
    ("Welche ist die Hauptstadt von Deutschland?", "de"),
    ("Ich liebe Kaffee und Gebäck", "de"),
    
    # Italien
    ("Ciao, come stai?", "it"),
    ("Qual è la capitale dell'Italia?", "it"),
    ("Mi piace il gelato", "it"),
    
    # Portugais
    ("Olá, como vai você?", "pt"),
    ("Qual é a capital de Portugal?", "pt"),
    ("Eu adoro café", "pt"),
    
    # Russe
    ("Привет, как дела?", "ru"),
    ("Какая столица России?", "ru"),
    
    # Arabe
    ("مرحبا، كيف حالك؟", "ar"),
    ("ما هي عاصمة مصر؟", "ar"),
    
    # Chinois
    ("你好，你好吗？", "zh"),
    ("中国的首都是什么？", "zh"),
    
    # Japonais
    ("こんにちは、お元気ですか？", "ja"),
    ("日本の首都は何ですか？", "ja"),
    
    # Coréen
    ("안녕하세요, 어떻게 지내세요?", "ko"),
    ("한국의 수도는 무엇입니까?", "ko"),
    
    # Accents spécifiques qui ne doivent pas être ambigus
    ("Ñoño, ¿qué pasa?", "es"),  # Espagnol avec ñ
    ("Não, obrigado", "pt"),  # Portugais avec ã, õ
    ("Müller, Köln, Düsseldorf", "de"),  # Allemand avec umlaut
]

print("=" * 80)
print("TEST DE DÉTECTION DE LANGUE - VÉRIFICATION 0% ERREUR")
print("=" * 80)
print()

passed = 0
failed = 0
failed_cases = []

for prompt, expected_lang in test_cases:
    detected_lang = detect_language(prompt)
    status = "✓ PASS" if detected_lang == expected_lang else "✗ FAIL"
    
    if detected_lang == expected_lang:
        passed += 1
    else:
        failed += 1
        failed_cases.append((prompt, expected_lang, detected_lang))
    
    print(f"{status} | Prompt: {prompt[:40]:40} | Expected: {expected_lang:3} | Got: {detected_lang:3}")

print()
print("=" * 80)
print(f"RÉSULTATS: {passed} PASSED, {failed} FAILED")
print(f"Accuracy: {100 * passed / (passed + failed):.1f}%")
print("=" * 80)

if failed > 0:
    print()
    print("FAILED CASES:")
    for prompt, expected, got in failed_cases:
        print(f"  - '{prompt}'")
        print(f"    Expected: {expected}, Got: {got}")
        print()

print()
print("=" * 80)
print("TEST DES INSTRUCTIONS DE LANGUE")
print("=" * 80)
print()

# Test that language instructions are strong and present for all detected languages
languages_tested = set(lang for _, lang in test_cases)

for lang in sorted(languages_tested):
    instruction = get_language_instruction(lang)
    is_strong = "ABSOLUTE RULE" in instruction or "RÈGLE ABSOLUE" in instruction or "CRITICAL" in instruction or "VÉRROUILLÉE" in instruction
    strength = "✓ STRONG" if is_strong else "✗ WEAK"
    print(f"{strength} | Language: {lang:3} | Instruction length: {len(instruction):3} chars")

print()
print("=" * 80)
if failed == 0:
    print("✓ ALL TESTS PASSED - 0% ERRORS!")
    sys.exit(0)
else:
    print(f"✗ {failed} TEST(S) FAILED")
    sys.exit(1)

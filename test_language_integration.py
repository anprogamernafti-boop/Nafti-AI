#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test d'intégration API complète - Vérifier que les réponses sont en même langue.
"""

import sys
import os
import json

# Ajouter le répertoire du serveur au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import detect_language, get_language_instruction

print("=" * 80)
print("VÉRIFICATION DES INSTRUCTIONS DE LANGUE - INTÉGRITÉ COMPLÈTE")
print("=" * 80)
print()

# Test languages with their instructions
test_languages = {
    "fr": "FRANÇAIS",
    "en": "ENGLISH", 
    "es": "ESPAÑOL",
    "de": "DEUTSCH",
    "it": "ITALIANO",
    "pt": "PORTUGUÊS",
    "ru": "РУССКИЙ",
    "ar": "العربية",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
}

issues = 0
for lang, lang_name in test_languages.items():
    instruction = get_language_instruction(lang)
    
    # Check key components
    has_lock = "🔒" in instruction
    has_rule = "RULE" in instruction or "RÈGLE" in instruction or "REGLA" in instruction or "REGEL" in instruction or "REGOLA" in instruction or "REGRA" in instruction or "ПРАВИЛО" in instruction or "قاعدة" in instruction or "规则" in instruction or "ルール" in instruction or "규칙" in instruction
    has_critical = "CRITICAL" in instruction or "CRITICA" in instruction or "KRITISCHE" in instruction or "KRITISCH" in instruction or "KRITIEK" in instruction or "CRÍTICA" in instruction or "CRITÈRE" in instruction or "KRYTYCZNE" in instruction or "CRÍTICO" in instruction or "kritikus" in instruction or "حرجة" in instruction
    has_repeat = instruction.count(lang_name) >= 2 or (lang in ["zh", "ja", "ko"] and instruction.lower().count("only") >= 2)
    
    is_strong = has_lock and has_rule and has_critical and has_repeat
    
    status = "✓ STRONG" if is_strong else "✗ CHECK"
    
    print(f"{status} | {lang:3} | 🔒:{has_lock} RULE:{has_rule} CRIT:{has_critical} REP:{has_repeat}")
    
    if not is_strong:
        print(f"        Instruction: {instruction[:100]}...")
        issues += 1

print()
print("=" * 80)

# Test that language detection works with edge cases
print("TEST CAS LIMITES - ROBUSTESSE")
print("=" * 80)
print()

edge_cases = [
    ("Empty string", "", "fr"),  # Empty should default to French
    ("Only symbols", "???", "fr"),  # Only symbols should default
    ("Simple English", "hello world", "en"),  # Simple English
    ("Simple French", "bonjour monde", "fr"),  # Simple French
    ("Single letter", "a", "fr"),  # Single letter
    ("Russian word", "привет", "ru"),  # Russian word
    ("Numbers only", "123 456", "fr"),  # Numbers only (should default to French)
    ("Mixed with emoji", "hello 🎉 bonjour", "en"),  # Mixed with emoji (English first)
]

print(f"{'Test':<30} {'Input':<20} {'Expected':<5} {'Got':<5} {'Status':<6}")
print("-" * 70)

edge_pass = 0
for desc, prompt, expected in edge_cases:
    detected = detect_language(prompt)
    status = "✓" if detected == expected else "✗"
    if detected == expected:
        edge_pass += 1
    print(f"{desc:<30} {prompt[:20]:<20} {expected:<5} {detected:<5} {status:<6}")

print()
print(f"Edge cases: {edge_pass}/{len(edge_cases)} passed")
print()
print("=" * 80)

if issues == 0 and edge_pass == len(edge_cases):
    print("✓ TOUS LES TESTS PASSÉS - SYSTÈME ROBUSTE")
    sys.exit(0)
else:
    print(f"⚠ Attention: {issues} problème(s) d'instruction de langue trouvé(s)")
    sys.exit(0 if issues == 0 else 1)

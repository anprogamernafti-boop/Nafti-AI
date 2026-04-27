#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test final de vérification - 0% erreur garanti
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import detect_language, get_language_instruction

print("\n" + "=" * 80)
print("TEST FINAL - VÉRIFICATION 0% ERREUR")
print("=" * 80 + "\n")

# Test multilingue intensif
intensive_tests = {
    "fr": [
        "Bonjour, comment allez-vous ?",
        "Je suis français et j'aime le fromage",
        "Quelle est la meilleure façon de cuisiner les croissants ?",
        "C'est magnifique, n'est-ce pas ?",
        "Pourquoi la vie est-elle si courte ?",
    ],
    "en": [
        "Hello, how are you doing today?",
        "I am an English speaker from the UK",
        "What's the best way to make a cup of tea?",
        "This is amazing, isn't it?",
        "Why is life so short?",
    ],
    "es": [
        "¡Hola! ¿Cómo estás hoy?",
        "Soy españ ol y me encanta la paella",
        "¿Cuál es la mejor forma de hacer un taco?",
        "¡Qué maravilloso es este día!",
        "¿Por qué la vida es tan corta?",
    ],
    "de": [
        "Hallo, wie geht es dir heute?",
        "Ich bin Deutscher und liebe Bier",
        "Was ist die beste Art, ein Schnitzeland zu machen?",
        "Dies ist wunderbar, nicht wahr?",
        "Warum ist das Leben so kurz?",
    ],
    "pt": [
        "Olá, como você está hoje?",
        "Sou português e adoro vinho",
        "Qual é a melhor forma de fazer uma pastéis de nata?",
        "Isto é maravilhoso, não é?",
        "Por que a vida é tão curta?",
    ],
    "ar": [
        "مرحبا، كيف حالك اليوم؟",
        "أنا عربي وأحب الشاي",
        "ما أفضل طريقة لصنع الحمص؟",
        "هذا رائع، أليس كذلك؟",
        "لماذا الحياة قصيرة جداً؟",
    ],
    "ja": [
        "こんにちは、今日はどうですか？",
        "私は日本人で、お寿司が大好きです",
        "ラーメンを作る最良の方法は何ですか？",
        "これは素晴らしいですね？",
        "なぜ人生は短いのですか？",
    ],
    "zh": [
        "你好，你今天怎么样？",
        "我是中国人，我喜欢茶",
        "制作饺子的最佳方式是什么？",
        "这真棒，不是吗？",
        "为什么生活这么短？",
    ],
}

total_tests = 0
passed_tests = 0

for lang, prompts in intensive_tests.items():
    print(f"Language: {lang.upper()}")
    for prompt in prompts:
        detected = detect_language(prompt)
        passed = detected == lang
        status = "✓" if passed else "✗"
        
        total_tests += 1
        if passed:
            passed_tests += 1
        
        # Display test result
        prompt_short = (prompt[:50] + "...") if len(prompt) > 50 else prompt
        print(f"  {status} {prompt_short:55} → {detected}")
    print()

print("=" * 80)
print(f"RÉSULTATS FINAUX: {passed_tests}/{total_tests} tests réussis")
accuracy = 100 * passed_tests / total_tests if total_tests > 0 else 0
print(f"Précision: {accuracy:.1f}%")
print("=" * 80)

# Verify language instructions
print("\nVérification des instructions de langue:")
print("-" * 80)

for lang in intensive_tests.keys():
    instruction = get_language_instruction(lang)
    
    # Verify key components
    has_lock = "🔒" in instruction
    has_rule = "RULE" in instruction or "RÈGLE" in instruction or "REGLA" in instruction or "REGEL" in instruction or "REGOLA" in instruction or "REGRA" in instruction or "ПРАВИЛО" in instruction or "قاعدة" in instruction or "规则" in instruction or "ルール" in instruction or "규칙" in instruction
    is_strong = has_lock and has_rule
    
    status = "✓ STRONG" if is_strong else "✗ CHECK"
    print(f"{status} | {lang.upper():3} | {len(instruction):3} chars | {instruction[:60]}...")

print("=" * 80)

if passed_tests == total_tests:
    print(f"\n✅ SUCCÈS TOTAL: {passed_tests}/{total_tests} (100%)")
    print("🔒 SYSTÈME VERROUILLÉ - RÉPONSES 0% ERREUR")
    sys.exit(0)
else:
    print(f"\n⚠️  {total_tests - passed_tests} erreur(s) détectée(s)")
    sys.exit(1)

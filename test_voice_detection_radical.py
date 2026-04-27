#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Test Script - Détection de Langue RADICALE
Vérifie que la détection fonctionne correctement pour l'arabe et les autres langues
"""

def test_language_detection():
    """Test les fonctions de détection de langue"""
    
    # Import depuis server.py
    import sys
    sys.path.insert(0, '/Users/Asser/Desktop/nafti-ai')
    
    from server import detect_language_ensemble
    
    # Test cases
    test_cases = [
        # ARABE - PRIORITAIRE
        ("السلام عليكم ورحمة الله وبركاته", "ar", "Arabe pur"),
        ("أنا أحب هذا التطبيق", "ar", "Phrase arabe simple"),
        ("مرحبا، كيف حالك؟", "ar", "Salutation arabe"),
        ("في، من، إلى، مع", "ar", "Petits mots arabes"),
        
        # Arabe + translittération
        ("مرحبا hello assalamu alaikum", "ar", "Arabe + English"),
        ("انا anta huwa she", "ar", "Arabe + translittération"),
        
        # FRANÇAIS
        ("Bonjour, comment allez-vous?", "fr", "Français pur"),
        ("Je suis très heureux de vous rencontrer", "fr", "Phrase française"),
        ("Merci beaucoup pour votre aide", "fr", "Merci français"),
        
        # ANGLAIS
        ("Hello, how are you today?", "en", "Anglais pur"),
        ("I love this application", "en", "Phrase anglaise"),
        ("Thank you very much", "en", "Remerciements anglais"),
        
        # ALLEMAND
        ("Guten Tag, wie geht es Ihnen?", "de", "Allemand pur"),
        ("Ich bin sehr glücklich", "de", "Phrase allemande"),
        
        # ESPAGNOL
        ("¡Hola! ¿Cómo estás?", "es", "Espagnol pur"),
        ("Me encanta este programa", "es", "Phrase espagnole"),
        
        # CYRILLIC (Russe)
        ("Привет, как дела?", "ru", "Russe pur"),
        
        # Texte vide
        ("", None, "Texte vide"),
        ("   ", None, "Espaces seulement"),
    ]
    
    print("=" * 80)
    print("🧪 TESTS - DÉTECTION DE LANGUE RADICALE")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for text, expected_lang, description in test_cases:
        try:
            result = detect_language_ensemble(text)
            detected_lang = result.get('language')
            confidence = result.get('confidence', 0)
            method = result.get('method', '?')
            
            # Vérifier le résultat
            if expected_lang is None:
                success = detected_lang is None or confidence < 0.5
            else:
                success = detected_lang == expected_lang or (expected_lang == 'ar' and detected_lang == 'ar')
            
            status = "✅ PASS" if success else "❌ FAIL"
            passed += 1 if success else 0
            failed += 0 if success else 1
            
            print(f"\n{status} | {description}")
            print(f"   Texte: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"   Attendu: {expected_lang:5s} | Détecté: {detected_lang:5s} | Confiance: {confidence:.2f} | Méthode: {method}")
            
        except Exception as e:
            print(f"\n❌ ERROR | {description}")
            print(f"   Exception: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 RÉSULTATS: {passed} PASS ✅ | {failed} FAIL ❌")
    print("=" * 80)
    
    return passed, failed

if __name__ == '__main__':
    try:
        passed, failed = test_language_detection()
        exit(0 if failed == 0 else 1)
    except ImportError as e:
        print(f"⚠️  Impossible d'importer server.py: {e}")
        print("Assurez-vous que vous exécutez ce script depuis le répertoire racine de nafti-ai")
        exit(1)

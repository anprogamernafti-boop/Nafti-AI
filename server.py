from flask import Flask, request, jsonify, send_file, send_from_directory, redirect, url_for, render_template, flash, session
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import os
import json
import hashlib
import uuid
import base64
import gc
import time
import re
from PIL import Image
from io import BytesIO
from langdetect import detect, LangDetectException, DetectorFactory
DetectorFactory.seed = 0   # Résultats reproductibles

# Autoriser OAuth en HTTP pour le développement local
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
from pathlib import Path
from datetime import datetime
from flask_dance.contrib.google import make_google_blueprint, google

# Charger les variables d'environnement depuis .env
load_dotenv()

print("[STARTUP] Flask app initializing...")
app = Flask(__name__, static_folder="static")
print("[STARTUP] Flask app created")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecret')
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
print("[STARTUP] CORS enabled")

# File-based user storage
USERS_FILE = Path('users.json')

# Chat history storage (supports multiple sessions per user)
HISTORY_FILE = Path('history.json')

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_history(data):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def _is_valid_session(entry):
    """Check if a history entry is a valid session object (has id, title, messages)."""
    return isinstance(entry, dict) and 'id' in entry and 'messages' in entry

def ensure_user_sessions(user):
    histories = load_history()
    if user not in histories:
        histories[user] = []
        save_history(histories)
    else:
        # Clean up any malformed entries (e.g. raw messages without session structure)
        original = histories[user]
        cleaned = [s for s in original if _is_valid_session(s)]
        if len(cleaned) != len(original):
            histories[user] = cleaned
            save_history(histories)
    return histories

def create_session_for_user(user):
    histories = ensure_user_sessions(user)
    new_id = str(uuid.uuid4())
    session_obj = {"id": new_id, "title": "Nouvelle conversation", "created_at": datetime.now().isoformat(), "messages": []}
    histories[user].append(session_obj)
    save_history(histories)
    return session_obj

def find_session(user, session_id):
    histories = ensure_user_sessions(user)
    for sess in histories.get(user, []):
        if sess.get('id') == session_id:
            return sess
    return None

def delete_session(user, session_id):
    histories = ensure_user_sessions(user)
    histories[user] = [s for s in histories.get(user, []) if s.get('id') != session_id]
    save_history(histories)

def load_users():
    """Load users from JSON file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def detect_language(text):
    """Détection de langue automatique — aucune sélection manuelle requise.

    Ordre de priorité :
      1. Scripts non-latins  → détection instantanée et sûre à 100 %
      2. Accents 100 % non-ambigus (ñ, ã, ä, ß…) → une seule langue possible
      3. langdetect (NLP) dès 1 mot → démêle FR/PT/IT/EN avec précision ~95 %
      4. Accents ambigus pour 1 seul mot court sans langdetect
      5. Mots-clés pondérés  → filet de sécurité pour textes ultra-courts
      6. Fallback fr         → langue par défaut de l'app
    """
    if not text or not text.strip():
        return "fr"

    stripped_text = text.strip()

    # ── 1. Scripts non-latins ────────────────────────────────────────────────
    if re.search(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]", stripped_text):
        return "ar"   # Arabe (tous blocs Unicode)
    if re.search(r"[\u0400-\u04FF]", stripped_text):
        return "ru"   # Cyrillique (russe, ukrainien…)
    # Japonais AVANT chinois : hiragana/katakana sont uniquement japonais
    if re.search(r"[\u3040-\u309F\u30A0-\u30FF]", stripped_text):
        return "ja"   # Japonais (hiragana + katakana)
    if re.search(r"[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]", stripped_text):
        return "zh"   # Chinois (simplifié / traditionnel / CJK compat.)
    if re.search(r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]", stripped_text):
        return "ko"   # Coréen (Hangul)
    if re.search(r"[\u0370-\u03FF\u1F00-\u1FFF]", stripped_text):
        return "el"   # Grec (+ grec étendu)
    if re.search(r"[\u0590-\u05FF\uFB1D-\uFB4F]", stripped_text):
        return "he"   # Hébreu
    if re.search(r"[\u0900-\u097F]", stripped_text):
        return "hi"   # Devanagari (hindi, marathi…)
    if re.search(r"[\u0E00-\u0E7F]", stripped_text):
        return "th"   # Thaï
    # Turc : caractères spécifiques (sans re.I → évite les faux positifs avec 'i' latin)
    if re.search(r"[ğışĞŞ\u0130\u0131]", stripped_text):
        return "tr"

    # ── 2. Accents 100 % non-ambigus ────────────────────────────────────────
    # Espagnol : ñ, ¿, ¡ → absents de toutes les autres langues latines
    if re.search(r"[ñ¿¡]", stripped_text):
        return "es"
    # Portugais : ã, õ → exclusifs au portugais (ã ≠ ā latin)
    if re.search(r"[ãõ]", stripped_text):
        return "pt"
    # Allemand : ä, ö, ü, ß → exclusifs à l'allemand
    if re.search(r"[äöüß]", stripped_text):
        return "de"
    # Polonais : ł, ź, ż, ą, ę, ć, ń, ś, ó (combinaison unique)
    if re.search(r"[łźżąęćńś]", stripped_text):
        return "pl"
    # Roumain : ș, ț (virgule sous lettre), ă, â diacritiques exclusifs au roumain
    if re.search(r"[șțȘȚăĂ]", stripped_text):
        return "ro"
    # Tchèque / Slovaque : ů, ě, č, š, ř, ž, ď, ť, ň
    if re.search(r"[ůěřďť]", stripped_text):
        return "cs"
    # Scandinave : å → danois/norvégien/suédois
    if re.search(r"[åÅ]", stripped_text):
        return "sv"   # par défaut suédois (le plus utilisé)

    # ── 3. langdetect (NLP) — dès 1 mot pour démêler FR/PT/IT/EN ────────────
    try:
        words = stripped_text.split()
        if len(words) >= 1:  # Activé dès le premier mot
            detected = detect(stripped_text)
            supported = {
                'fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'ar',
                'zh-cn', 'zh-tw', 'ja', 'ko', 'nl', 'tr', 'pl',
                'sv', 'da', 'fi', 'cs', 'hu', 'ro', 'el', 'he',
                'hi', 'th', 'vi', 'id', 'ms', 'uk', 'ca', 'gl'
            }
            if detected in supported:
                return "zh" if detected.startswith("zh") else detected
            # Gestion des variantes de codes (ex: zh-cn → zh)
            base = detected.split('-')[0]
            if base in supported:
                return base
    except Exception:
        pass

    # ── 4. Accents ambigus pour textes courts (sans résultat langdetect fiable) ─
    # Français exclusif : œ, æ, â, ê, î, ô, û, ë, ï, ù, ÿ
    if re.search(r"[àâçèêëîïôùûüÿœæ]", stripped_text, flags=re.IGNORECASE):
        return "fr"
    # Accent aigu ambigu (á, é, í, ó, ú) : présent en ES, PT, IT
    # → résolution par mots-clés avant de tomber sur un défaut
    if re.search(r"[áéíóú]", stripped_text, flags=re.IGNORECASE):
        lower_accented = stripped_text.lower()
        # Portugais : mots très distinctifs (tudo, você, não, obrigado…)
        pt_signals = re.findall(
            r"\b(tudo|voce|nao|obrigado|obrigada|ola|pois|embora|tenho|temos"
            r"|tambem|isso|aqui|entao|muito|agora|estou|estao|posso|podes)\b",
            lower_accented)
        # Espagnol : mots très distinctifs (hola, hay, también, vosotros…)
        es_signals = re.findall(
            r"\b(hola|hay|vosotros|ellos|ellas|del|bueno|claro|vale|pues"
            r"|tiene|tienes|tienen|quiero|quieres|puedo|puedes|pueden|estoy|estas|estan)\b",
            lower_accented)
        # Italien : mots distinctifs (ciao, sono, avere, essere…)
        it_signals = re.findall(
            r"\b(ciao|sono|avere|essere|grazie|scusa|prego|bene|tutto|molto"
            r"|ho|hai|ha|abbiamo|voglio|vuoi|siamo|cosa|chi|dove)\b",
            lower_accented)
        if len(pt_signals) >= len(es_signals) and len(pt_signals) >= len(it_signals) and pt_signals:
            return "pt"
        if len(it_signals) > len(es_signals) and len(it_signals) > len(pt_signals):
            return "it"
        return "es"  # défaut pour les accents aigus sans contexte
    # Italien : ì exclusif (più, così…)
    if re.search(r"[ìÌ]", stripped_text, flags=re.IGNORECASE):
        return "it"

    # ── 5. Mots-clés pondérés (textes très courts ≤ 1 mot, sans accents) ────
    lower_text = stripped_text.lower()

    kw = {
        # Français : mots grammaticaux + salutations très fréquents
        "fr": r"\b(je|tu|il|elle|nous|vous|ils|elles|un|une|des|les|le|la|est|sont"
              r"|avec|pour|dans|sur|par|mais|donc|car|or|ni|si|que|qui|quoi"
              r"|salut|bonjour|bonsoir|coucou|merci|oui|non|svp|ici|tres|bien|aussi|alors"
              r"|comment|pourquoi|quand|faire|avoir|aller|vouloir|pouvoir|devoir|venir|voir"
              r"|sans|vers|sous|entre|depuis|avant|apres|toujours|jamais|encore|deja"
              r"|mon|ma|mes|ton|ta|tes|son|sa|ses|notre|votre|leur|leurs)\b",

        # Anglais : mots fréquents, évite les collisions avec FR (a, an, or, for…)
        "en": r"\b(i|you|he|she|we|they|the|is|are|was|were|be|been|being"
              r"|have|has|had|do|does|did|will|would|could|should|may|might|shall"
              r"|and|but|not|this|that|these|those|with|from|into|about|just|also"
              r"|hi|hello|hey|thanks|thank|yes|no|please|sorry|okay|ok|sure|right"
              r"|what|who|where|when|why|how|can|my|your|his|her|our|their|its"
              r"|get|got|go|come|know|think|make|take|want|need|see|look|use|find)\b",

        # Espagnol : mots exclusifs (évite les collisions avec PT)
        "es": r"\b(yo|nosotros|vosotros|ellos|ellas|los|las|del|al"
              r"|con|para|por|pero|aunque|mientras|porque|entonces"
              r"|hola|adios|gracias|por favor|perdon|bueno|claro|vale|pues"
              r"|hacer|ir|venir|tener|estar|ser|poder|querer|deber|saber|ver|dar)\b",

        # Allemand : mots grammaticaux typiques + salutations sans accents
        "de": r"\b(ich|du|er|wir|ihr|der|die|das|ein|eine|und|ist|sind|war|waren"
              r"|mit|fur|auf|an|von|zu|bei|nach|uber|unter|vor|hinter|neben"
              r"|hallo|danke|ja|nein|bitte|wie|was|wo|wer|warum|wann|schon|noch"
              r"|morgen|abend|guten|gut|tag|nacht|tschuss|entschuldigung"
              r"|machen|gehen|kommen|haben|sein|werden|konnen|mussen|wollen|sagen)\b",

        # Portugais : mots exclusifs vs espagnol (nós, eles, não, mas, porque…)
        "pt": r"\b(eu|nos|eles|elas|um|uma|os|as|do|da|dos|das|num|numa"
              r"|com|para|em|por|mas|se|como|quando|porque|pois|embora"
              r"|ola|obrigado|obrigada|sim|nao|por favor|desculpe|tudo|bem|voce"
              r"|fazer|ir|vir|ter|estar|ser|poder|querer|dever|saber|ver|dar"
              r"|tenho|tens|tem|temos|quero|queres|posso|podes|estou|estao|isso|tambem)\b",

        # Italien : mots exclusifs
        "it": r"\b(io|lui|lei|noi|loro|il|gli|uno|una|del|della|degli|delle"
              r"|con|per|su|di|che|ma|se|come|quando|perche|quindi|pero|anche"
              r"|ciao|grazie|scusa|prego|si|no|per favore|bene|tutto|molto"
              r"|fare|andare|venire|avere|essere|potere|volere|dovere|sapere|vedere|dare)\b",

        # Néerlandais : mots typiques
        "nl": r"\b(ik|jij|jij|hij|zij|wij|jullie|de|het|een|zijn|was|waren"
              r"|met|voor|op|aan|van|naar|bij|over|door|onder|maar|ook|nog|al"
              r"|hallo|dag|dank|ja|nee|alsjeblieft|sorry|goed|hoe|wat|wie|waar|waarom"
              r"|maken|gaan|komen|hebben|zijn|worden|kunnen|moeten|willen|zeggen)\b",

        # Arabe romanisé (translittéré) → très courant dans le Maghreb
        "ar": r"\b(marhaba|ahlan|salamalaikum|shukran|afwan|inshallah|habibi|yalla"
              r"|kifak|kifek|wesh|labas|bghit|nta|nti|hna|ntuma|ana|hwa|hya"
              r"|choukran|mersi|saha|baraka|mabrook|ach|wach|fain|mnin|bikhir)\b",
    }

    scores = {}
    for lang, pattern in kw.items():
        matches = re.findall(pattern, lower_text, flags=re.IGNORECASE)
        scores[lang] = len(matches)

    if scores:
        best_lang = max(scores, key=scores.get)
        # Seuil minimal de 1 correspondance + avantage FR en cas d'ex-aequo
        if scores[best_lang] >= 1:
            # En cas d'égalité, préférer le français (langue par défaut de l'app)
            top_score = scores[best_lang]
            candidates = [l for l, s in scores.items() if s == top_score]
            if len(candidates) == 1:
                return best_lang
            elif "fr" in candidates:
                return "fr"
            else:
                return candidates[0]

    # ── 6. Fallback ──────────────────────────────────────────────────────────
    return "fr"  # Langue par défaut de l'app


def detect_tunisian_dialect(text):
    """Detect if the user specifically requests Tunisian dialect in Arabic or French."""
    if not text:
        return None

    lower_text = text.lower()
    arabic_script = bool(re.search(r"[\u0600-\u06FF]", text))

    dialect_terms = [
        "dialecte tunisien",
        "arabe tunisien",
        "tunisien",
        "tunisie",
        "tounsi",
        "darija",
        "darja",
        "derja",
    ]

    french_tunisian_terms = [
        "tawa", "briki", "barcha", "mouch", "chwaya", "ya3ni", "kifech",
        "chnowa", "chna", "sahha", "beldi", "hakka", "nchallah", "ma nhebch",
        "ma nhebich", "tawa", "hakka", "kif ken", "fik", "slama", "barsha"
    ]

    arabic_tunisian_terms = [
        # Pronoms et questions
        "شنية", "شنيا", "شنو", "شنوة", "شنوا", "شنا", "شنو", "شنية", "شكون", "شكوني", "شكونك", "شكونو", "شكوننا",
        # Endroits et choses
        "بلاص", "بلايص", "بلاصة", "بلاصات", "بلاصي", "بلاصك", "بلاصو", "بلاصنا", "حاجة", "حاجتي", "حاجتك", "حاجتو", "حاجتنا",
        # Verbes courants
        "تنجم", "تنجيم", "تنجمي", "تنجمش", "تنجمو", "نجم", "نجيم", "تزور", "تزوري", "تزورش", "تزورو", "زور", "زوري", "زورش", "زورو",
        "تعمل", "تعملي", "تعملش", "تعملو", "عمل", "عملي", "عملش", "عملو", "تكتب", "تكتبي", "تكتبش", "تكتبو", "كتب", "كتبي", "كتبش", "كتبو",
        "تفهم", "تفهمي", "تفهمش", "تفهمو", "فهم", "فهمي", "فهمش", "فهمو", "تقول", "تقولي", "تقولش", "تقولو", "قال", "قالت", "قالو",
        # Expressions de temps et lieu
        "توا", "تواتي", "تواتك", "تواتو", "تواتنا", "بالحق", "بالحقي", "بالحقك", "بالحقو", "بالحقنا", "هناك", "هون", "هونيك", "هونيكي",
        # Adjectifs et adverbes
        "يزي", "يزيك", "يزيو", "يزينا", "بربي", "بربيك", "بربيو", "بربينا", "صحيت", "صحيتي", "صحيتك", "صحيتو", "صحيتنا",
        "عاوني", "عاونك", "عاونو", "عاوننا", "شيم", "شيمي", "شيمك", "شيمو", "شيمنا", "موش", "موشي", "موشك", "موشو", "موشنا",
        # Négations et particules
        "ما", "ماش", "ماشي", "ماشك", "ماشو", "ماشنا", "ما نعرفش", "ما نعرفيش", "ما نعرفوش", "ما نعرفوش", "ما نقدرش", "ما نقدريش", "ما نقدروش",
        # Salutations et expressions courantes
        "عسلامة", "عسلامتي", "عسلامتو", "عسلامتك", "عسلامته", "مرحبا", "أهلا", "سلام", "سلامو", "كيفاش", "كيفك", "كيفيك", "كيفو", "كيفنا",
        "شخبارك", "شخباري", "شخبارو", "شخبارنا", "إزيك", "إزي", "إزيو", "إزينا", "الحمد لله", "بخير", "تمام", "ماشي الحال",
        # Nombres et quantités
        "واحد", "وحدة", "زوز", "تلاتة", "أربعة", "خمسة", "ستة", "سبعة", "تمنية", "تسعة", "عشرة", "كتير", "شوية", "قليل", "برشة", "برش", "برشي", "برشك", "برشو",
        # Mots de liaison et particules
        "و", "أو", "لكن", "باش", "علاش", "عشان", "بسبب", "مع", "ماع", "في", "فيك", "فيو", "فينا", "على", "عند", "عندي", "عندك", "عندو", "عندنا",
        # Expressions d'accord et désaccord
        "أي", "أيوا", "إيه", "صح", "صحيح", "ماشي", "تمام", "موافق", "موافقش", "ما موافقش", "خايب", "خايبة", "خايبين", "زعطة", "زعاطة",
        # Mots d'émotion et d'exclamation
        "يا", "ياخي", "ياخيتي", "ياخيتو", "ياخيتك", "ياخيته", "ربي", "ربيك", "ربيو", "ربينا", "بربي", "بربيك", "بربيو", "بربينا",
        "الله", "والله", "بالله", "إنشاء الله", "إن شاء الله", "نعرفش", "ما نعرفش", "شكون يعرف", "يعرف", "يعرفي", "يعرفش", "يعرفو",
        # Mots liés à la nourriture et boissons
        "كسكسي", "كسكس", "ملوخية", "شوربة", "حريرة", "بريك", "بريكي", "بريكش", "بريكو", "عجينة", "عجينتي", "عجينتو", "عجينتك", "عجينته",
        "قهوة", "قهوتي", "قهوتك", "قهوتو", "قهوتنا", "شاي", "شايي", "شايك", "شايو", "شاينا", "عصير", "عصيري", "عصيرك", "عصيرو", "عصيرنا",
        # Mots liés au transport et déplacements
        "تمشي", "تمشيي", "تمشيش", "تمشيو", "مشى", "مشيت", "مشيش", "مشيو", "تروح", "تروحي", "تروحش", "تروحو", "روح", "روحي", "روحش", "روحو",
        "تيجي", "تيجيي", "تيجيش", "تيجيو", "جاء", "جيت", "جيش", "جيو", "لوطو", "لوطي", "لوطك", "لوطو", "لوطنا",
        # Mots liés au travail et études
        "تشتغل", "تشتغلي", "تشتغلش", "تشتغلو", "اشتغل", "اشتغلت", "اشتغلش", "اشتغلو", "تقرأ", "تقرئي", "تقرئش", "تقرئو", "قرأ", "قريت", "قريش", "قريو",
        "تدرس", "تدرسي", "تدرسش", "تدرسو", "درس", "درست", "درسش", "درسو", "تفهم", "تفهمي", "تفهمش", "تفهمو", "فهم", "فهمت", "فهمش", "فهمو",
        # Expressions temporelles
        "اليوم", "بكري", "مساء", "ليل", "نهار", "صباح", "عشية", "أمس", "غدا", "بعد غدا", "قبل غدا", "كل يوم", "كل نهار", "كل ليل", "دائما", "أبدا",
        # Mots liés à la famille
        "بابا", "ماما", "خالي", "خالتي", "عمي", "عمتي", "جدي", "جدتي", "ولد", "ولدي", "ولدك", "ولدو", "ولدنا", "بنت", "بنتي", "بنتك", "بنتو", "بنتنا",
        # Mots liés à l'argent et commerce
        "فلوس", "فلوسي", "فلوسك", "فلوسو", "فلوسنا", "دراهم", "دراهمي", "دراهمك", "دراهمو", "دراهمنا", "غالي", "غالية", "غاليين", "رخيص", "رخيصة", "رخيصين",
        "يشتري", "يشتريي", "يشتريش", "يشتريو", "اشترى", "اشتريت", "اشتريش", "اشتريو", "يبيع", "يبيعي", "يبيعش", "يبيعو", "باع", "بعت", "بيعش", "بيعو",
        # Mots supplémentaires courants
        "أحسن", "أحسني", "أحسنك", "أحسنو", "أحسنا", "جميل", "جميلة", "جميلين", "قبيح", "قبيحة", "قبيحين", "سريع", "سريعة", "سريعين", "بطيء", "بطيئة", "بطيئين",
        "كبير", "كبيرة", "كبار", "صغير", "صغيرة", "صغار", "جديد", "جديدة", "جدد", "قديم", "قديمة", "قدماء", "ساخن", "ساخنة", "ساخنين", "بارد", "باردة", "باردين",
        "طويل", "طويلة", "طوال", "قصير", "قصيرة", "قصار", "عالي", "عالية", "عالين", "منخفض", "منخفضة", "منخفضين", "قوي", "قوية", "أقوياء", "ضعيف", "ضعيفة", "ضعفاء",
        "سهل", "سهلة", "سهلين", "صعب", "صعبة", "صعبين", "ممكن", "ممكنة", "ممكنين", "مستحيل", "مستحيلة", "مستحيلين", "حلو", "حلوة", "حلال", "مر", "مرة", "مرور",
        "أبيض", "أبيضة", "بيض", "أسود", "أسودة", "سود", "أحمر", "أحمرة", "حمور", "أخضر", "أخضرة", "خضور", "أزرق", "أزرقة", "زرق", "أصفر", "أصفرة", "صفر",
        "أول", "تاني", "تالت", "رابع", "خامس", "سادس", "سابع", "تامن", "تاسع", "عاشر", "أخير", "أخيرة", "أخيرين", "أول", "أولى", "أوائل", "وسط", "وسطي", "وسطيين",
        "قدام", "ورا", "فوق", "تحت", "جنب", "بين", "معا", "وحيد", "وحيدة", "وحيدين", "كل", "كلشي", "شيء", "شيئي", "شيئك", "شيئو", "شيئنا", "لا شيء", "ولا شيء",
        "كيف", "كيفاش", "كيفك", "كيفيك", "كيفو", "كيفنا", "متاع", "متاعي", "متاعك", "متاعو", "متاعنا", "تابع", "تابعة", "تابعين", "منفصل", "منفصلة", "منفصلين",
        "مباشر", "مباشرة", "مباشرين", "غير مباشر", "غير مباشرة", "غير مباشرين", "مختلف", "مختلفة", "مختلفين", "نفس", "نفسها", "نفسهم", "مثل", "مثلك", "مثلو", "مثلنا",
        "أكثر", "أكثري", "أكثرك", "أكثرو", "أكثرنا", "أقل", "أقلي", "أقلك", "أقلو", "أقلنا", "أحسن", "أحسني", "أحسنك", "أحسنو", "أحسنا", "أسوأ", "أسوئي", "أسوئك", "أسوئو", "أسوئنا",
        "جيد", "جيدة", "جيدين", "سيء", "سيئة", "سيئين", "ممتاز", "ممتازة", "ممتازين", "عادي", "عادية", "عاديين", "رائع", "رائعة", "رائعين", "فظيع", "فظيعة", "فظيعين",
        "مهم", "مهمة", "مهمين", "غير مهم", "غير مهمة", "غير مهمين", "ضروري", "ضرورية", "ضروريين", "اختياري", "اختيارية", "اختياريين", "مفيد", "مفيدة", "مفيدين", "غير مفيد", "غير مفيدة", "غير مفيدين",
        "ممتع", "ممتعة", "ممتعين", "مضجر", "مضجرة", "مضجرين", "مثير", "مثيرة", "مثيرين", "ممل", "مملة", "مملين", "مفاجئ", "مفاجئة", "مفاجئين", "متوقع", "متوقعة", "متوقعين",
        "صادق", "صادقة", "صادقين", "كاذب", "كاذبة", "كاذبين", "ذكي", "ذكية", "ذكيين", "غبي", "غبية", "غبيين", "ودود", "ودودة", "ودودين", "عدواني", "عدوانية", "عدوانيين",
        "صبور", "صبورة", "صبورين", "عصبي", "عصبية", "عصبيين", "هادئ", "هادئة", "هادئين", "عصبي", "عصبية", "عصبيين", "نشيط", "نشيطة", "نشيطين", "كسول", "كسولة", "كسالى",
        "غني", "غنية", "أغنياء", "فقير", "فقيرة", "فقراء", "سعيد", "سعيدة", "سعداء", "حزين", "حزينة", "أحزان", "مضحك", "مضحكة", "مضحكين", "جدي", "جدية", "جديين",
        "شجاع", "شجاعة", "شجعان", "جبان", "جبانة", "جبناء", "قوي", "قوية", "أقوياء", "ضعيف", "ضعيفة", "ضعفاء", "صحي", "صحية", "صحيين", "مريض", "مريضة", "مرضى",
        "شاب", "شابة", "شباب", "عجوز", "عجوزة", "عجائز", "طويل", "طويلة", "طوال", "قصير", "قصيرة", "قصار", "نحيف", "نحيفة", "نحفاء", "سمين", "سمينة", "سمان",
        "جميل", "جميلة", "جمال", "قبيح", "قبيحة", "قبح", "أنيق", "أنيقة", "أناقة", "مهمل", "مهملة", "مهملين", "نظيف", "نظيفة", "نظفاء", "قذر", "قذرة", "أقذار",
        "حار", "حارة", "حرار", "بارد", "باردة", "برود", "رطب", "رطبة", "رطوبة", "جاف", "جافة", "جفاف", "مشمس", "مشمسة", "مشمسين", "غائم", "غائمة", "غيوم",
        "مظلم", "مظلمة", "ظلام", "مضيء", "مضيئة", "إضاءة", "هادئ", "هادئة", "هدوء", "صاخب", "صاخبة", "صخب", "مزدحم", "مزدحمة", "ازدحام", "فارغ", "فارغة", "فراغ",
        "بعيد", "بعيدة", "بعد", "قريب", "قريبة", "قرب", "سريع", "سريعة", "سرعة", "بطيء", "بطيئة", "بطء", "سهل", "سهلة", "سهولة", "صعب", "صعبة", "صعوبة",
        "رخيص", "رخيصة", "رخص", "غالي", "غالية", "غلاء", "مجاني", "مجانية", "مجانيين", "مدفوع", "مدفوعة", "مدفوعين", "متوفر", "متوفرة", "متوفرين", "نادر", "نادرة", "نذور",
        "مثالي", "مثالية", "مثاليين", "كامل", "كاملة", "كمال", "ناقص", "ناقصة", "نقص", "مستقل", "مستقلة", "استقلال", "تابع", "تابعة", "تبعية", "حر", "حرة", "أحرار",
        "محظور", "محظورة", "محظورين", "مسموح", "مسموحة", "مسموحين", "ضروري", "ضرورية", "ضروريين", "اختياري", "اختيارية", "اختياريين", "مهم", "مهمة", "مهمين", "ثانوي", "ثانوية", "ثانويين"
    ]

    if arabic_script:
        # Check for explicit dialect terms
        if any(term in lower_text for term in dialect_terms):
            return "ar"
        # Check for Tunisian Arabic terms
        if any(term in text for term in arabic_tunisian_terms):
            return "ar"
    else:
        if any(term in lower_text for term in french_tunisian_terms) or any(term in lower_text for term in dialect_terms):
            return "fr"

    return None
def get_language_instruction(lang_code, prompt_text=None):
    """Instructions système fermes pour forcer la langue de réponse"""
    
    # Gestion du dialecte tunisien (gardez votre logique existante)
    if lang_code == "ar" and prompt_text:
        tunisian_dialect = detect_tunisian_dialect(prompt_text)
        if tunisian_dialect == "ar":
            specific_tunisian_terms = ['شنية', 'شكون', 'بالحق', 'يزي', 'بربي', 'ما نعرفش']
            if any(term in prompt_text for term in specific_tunisian_terms):
                return "RÈGLE ABSOLUE : Tu dois OBLIGATOIREMENT répondre en arabe tunisien authentique (derja). N'utilise AUCUNE autre langue."

    if lang_code == "fr" and prompt_text:
        if detect_tunisian_dialect(prompt_text) == "fr":
            return "RÈGLE ABSOLUE : Tu dois OBLIGATOIREMENT répondre en français tunisien authentique (derja). N'utilise AUCUNE autre langue."

    # Instructions fermes pour les autres langues
    instructions = {
        "fr": "RÈGLE ABSOLUE : Tu dois OBLIGATOIREMENT répondre en FRANÇAIS. N'utilise AUCUNE autre langue.",
        "en": "ABSOLUTE RULE: You MUST respond ONLY in ENGLISH. Do NOT use any other language.",
        "ar": "قاعدة مطلقة: يجب عليك الرد باللغة العربية فقط. لا تستخدم أي لغة أخرى.",
        "es": "REGLA ABSOLUTA: Debes responder ÚNICAMENTE en ESPAÑOL. NO uses ningún otro idioma.",
        "de": "ABSOLUTE REGEL: Du MUSST AUSSCHLIESSLICH auf DEUTSCH antworten. Verwende KEINE andere Sprache.",
        "it": "REGOLA ASSOLUTA: Devi rispondere ESCLUSIVAMENTE in ITALIANO. NON usare nessun'altra lingua.",
        "pt": "REGRA ABSOLUTA: Você DEVE responder EXCLUSIVAMENTE em PORTUGUÊS. NÃO use nenhum outro idioma.",
        "ru": "АБСОЛЮТНОЕ ПРАВИЛО: Вы ДОЛЖНЫ отвечать ИСКЛЮЧИТЕЛЬНО на РУССКОМ языке. НЕ используйте никакой другой язык.",
        "zh": "绝对规则：你必须仅用中文回答。不要使用任何其他语言。",
        "ja": "絶対ルール：日本語のみで回答してください。他の言語は一切使用しないでください。",
        "ko": "절대 규칙: 한국어로만 답변해야 합니다. 다른 언어는 절대 사용하지 마세요.",
    }
    
    return instructions.get(lang_code, "ABSOLUTE RULE: You MUST respond ONLY in ENGLISH. Do NOT use any other language.")

    # For French, check for Tunisian dialect
    if lang_code == "fr" and prompt_text:
        tunisian_dialect = detect_tunisian_dialect(prompt_text)
        if tunisian_dialect == "fr":
            return "Répondez en français tunisien authentique (derja), comme un Tunisien qui parle naturellement. Utilisez des expressions tunisiennes courantes comme 'chwaya', 'ya3ni', 'tawa', 'barcha', 'mouch', 'kifech', 'chnowa', 'sahha', 'beldi', 'hakka', 'nchallah', 'ma nhebch', 'fik', 'slama', 'barsha', etc. Soyez amical et utilisez le style de conversation tunisien naturel."

    instructions = {
        "fr": "Répondez en français.",
        "en": "Respond in English.",
        "es": "Responde en español.",
        "de": "Antworte auf Deutsch.",
        "it": "Rispondi in italiano.",
        "pt": "Responda em português.",
        "ru": "Отвечайте на русском языке.",
        "ja": "日本語で答えてください。",
        "ko": "한국어로 답변해 주세요.",
        "zh": "请用中文回答。",
        "zh-cn": "请用中文回答。",
        "zh-tw": "請用中文回答。",
        "ar": "أجب باللغة العربية.",
        "hi": "हिंदी में जवाब दें।",
        "nl": "Reageer in het Nederlands.",
        "sv": "Svara på svenska.",
        "da": "Svar på dansk.",
        "no": "Svar på norsk.",
        "fi": "Vasta suomeksi.",
        "pl": "Odpowiedz po polsku.",
        "tr": "Türkçe cevap verin.",
        "he": "ענה בעברית.",
        "th": "ตอบเป็นภาษาไทย.",
        "vi": "Trả lời bằng tiếng Việt.",
        "cs": "Odpovězte česky.",
        "hu": "Válaszoljon magyarul.",
        "ro": "Răspundeți în română.",
        "sk": "Odpovedzte po slovensky.",
        "sl": "Odgovorite v slovenščini.",
        "hr": "Odgovorite na hrvatskom.",
        "bg": "Отговорете на български.",
        "uk": "Відповідайте українською.",
        "el": "Απαντήστε στα ελληνικά.",
        "et": "Vasta eesti keeles.",
        "lv": "Atbildiet latviešu valodā.",
        "lt": "Atsakykite lietuviškai.",
        "mt": "Wieġeb bil-Malti.",
        "ga": "Freagair as Gaeilge.",
        "cy": "Atebwch yn Gymraeg.",
        "is": "Svaraðu á íslensku.",
        "fo": "Svara á føroyskum.",
        "kl": "Apeqqut kalaallisut.",
        "sq": "Përgjigju në shqip.",
        "mk": "Одговорете на македонски.",
        "sr": "Одговорите на српском.",
        "bs": "Odgovorite na bosanskom.",
        "me": "Odgovorite na crnogorskom.",
        "sh": "Odgovorite na srpskohrvatskom.",
    }
    
    return instructions.get(lang_code, "Respond in English.")

# Configuration Groq (lue depuis .env)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Configuration HF Inference API (image generation - no local model needed on HF Spaces)
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-2-1")
HF_API_KEY = os.getenv("HF_API_KEY", "")  # Optional, uses free tier if not provided
HF_API_URL = "https://router.huggingface.co/models"  # Updated from api-inference.huggingface.co

# Global pipeline (loaded once, reused) - ONLY for local development
image_pipeline = None

def generate_placeholder_image(prompt, width=512, height=512):
    """Generate a simple placeholder image with gradient and text (optimized for memory)"""
    try:
        import numpy as np
    except ImportError:
        # Fallback if numpy not available
        import random
        from PIL import ImageDraw, ImageFont
        
        color_map = {
            'red': (255, 100, 100), 'blue': (100, 150, 255), 'green': (100, 255, 100),
            'yellow': (255, 255, 100), 'purple': (200, 100, 255), 'pink': (255, 150, 200),
        }
        
        prompt_lower = prompt.lower()
        base_color = (100, 100, 150)
        for keyword, color in color_map.items():
            if keyword in prompt_lower:
                base_color = color
                break
        
        img = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(img)
        text = prompt[:50]
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = max(10, (width - text_width) // 2)
        y = max(10, (height - text_height) // 2)
        
        for adj_x in [-1, 0, 1]:
            for adj_y in [-1, 0, 1]:
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        return img
    
    from PIL import ImageDraw, ImageFont
    
    # Color mapping for keywords
    color_map = {
        'red': (255, 100, 100), 'blue': (100, 150, 255), 'green': (100, 255, 100),
        'yellow': (255, 255, 100), 'purple': (200, 100, 255), 'pink': (255, 150, 200),
        'orange': (255, 165, 100), 'sky': (135, 206, 235), 'sea': (70, 130, 180),
    }
    
    # Determine base color from prompt keywords
    prompt_lower = prompt.lower()
    base_color = (100, 100, 150)
    for keyword, color in color_map.items():
        if keyword in prompt_lower:
            base_color = color
            break
    
    # Create gradient using numpy (much faster than pixel loops)
    # Allocate RGB array
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient efficiently
    for y in range(height):
        grad_factor = y / max(1, height - 1)
        r = min(255, base_color[0] + int(grad_factor * 30))
        g = min(255, base_color[1] + int(grad_factor * 20))
        b = min(255, base_color[2] + int(grad_factor * 40))
        
        # Set entire row with horizontal variation (vectorized)
        for x in range(width):
            x_var = int(x * 20 / width)
            img_array[y, x] = [
                max(0, r - x_var),
                max(0, g - x_var),
                max(0, b - x_var)
            ]
    
    # Convert numpy array to PIL Image
    img = Image.fromarray(img_array, 'RGB')
    
    # Add text
    draw = ImageDraw.Draw(img)
    text = prompt[:60]
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    # Draw text with outline
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = max(10, (width - text_width) // 2)
    y = max(10, (height - text_height) // 2)
    
    # Black outline
    for adj_x in [-1, 0, 1]:
        for adj_y in [-1, 0, 1]:
            if adj_x != 0 or adj_y != 0:
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=(0, 0, 0))
    # White text
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    return img

def get_image_pipeline():
    """Load image pipeline (lazy load - only for local development)"""
    global image_pipeline
    if image_pipeline is None:
        try:
            import torch
            from diffusers import StableDiffusionPipeline
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"📦 Loading Stable Diffusion 2.1 on {device}...")
            
            # Try with offline mode first, then Fall back to standard loading
            import os
            offlineMode = os.environ.get('HF_OFFLINE', '0') == '1'
            
            image_pipeline = StableDiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-2-1",
                torch_dtype=torch.float32,
                local_files_only=offlineMode
            )
            image_pipeline.to(device)
            print(f"✅ Model loaded on {device}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("📝 Falling back to placeholder image generation")
            return None
    return image_pipeline

# Google OAuth blueprint (try to register, but don't block startup if credentials missing)
try:
    if os.getenv('GOOGLE_CLIENT_ID') and os.getenv('GOOGLE_CLIENT_SECRET'):
        google_bp = make_google_blueprint(
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scope=["profile", "email"],
            redirect_url="/google_callback"
        )
        app.register_blueprint(google_bp, url_prefix="/login")
        print("✅ Google OAuth configured")
    else:
        print("⚠️  Google OAuth not configured (missing credentials)")
except Exception as e:
    print(f"⚠️  Google OAuth error (startup won't block): {e}")

# --- routes ---
@app.route("/health", methods=["GET", "HEAD"])
def health():
    """Health check endpoint for HF Spaces - MUST respond immediately"""
    try:
        return jsonify({"status": "ok", "service": "Nafti AI"}), 200
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 503

@app.route("/healthz", methods=["GET", "HEAD"])
def healthz():
    """Alternative health check endpoint"""
    return "OK", 200

print("[STARTUP] Health endpoints registered")
print("[STARTUP] ✅ Flask app ready for requests!")

# Request tracking to detect hangs
@app.before_request
def track_request():
    """Log all incoming requests for debugging"""
    request.start_time = time.time()
    # Only log non-health endpoints to avoid spam
    if request.path not in ['/health', '/healthz']:
        print(f"[REQUEST] -> {request.method} {request.path}")

@app.after_request
def track_response(response):
    """Log response times"""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        # Only log non-health endpoints
        if request.path not in ['/health', '/healthz'] and duration > 0.1:
            print(f"[REQUEST] <- {request.method} {request.path} {response.status_code} ({duration:.2f}s)")
    return response

@app.route("/")
def index():
    """Render the main template; template passes chat sessions list"""
    user = session.get('user')
    sessions = []
    if user:
        histories = ensure_user_sessions(user)
        sessions = histories.get(user, [])
    response = app.make_response(render_template('index.html', sessions=sessions))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/generate-image')
def generate_image():
    """Render the image generation page"""
    return render_template('generate.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        flash("Email et mot de passe requis")
        return redirect(url_for('index'))

    users = load_users()
    if email in users:
        flash("Email déjà utilisé")
        return redirect(url_for('index'))

    users[email] = {
        'password_hash': hash_password(password),
        'google_id': None
    }
    save_users(users)
    session['user'] = email
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    users = load_users()

    if email not in users or not verify_password(password, users[email]['password_hash']):
        flash("Identifiants invalides")
        return redirect(url_for('index'))

    session['user'] = email
    return redirect(url_for('index'))

@app.route('/settings')
def settings_view():
    return render_template('settings.html')

@app.route('/sessions/clear-all', methods=['POST'])
def clear_all_sessions():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Login to use AI features"}), 401
    histories = load_history()
    histories[user] = []
    save_history(histories)
    return jsonify({"status": "cleared"})

@app.route('/history')
def history_view():
    user = session.get('user')
    histories = load_history()
    sessions = histories.get(user, []) if user else []
    return render_template('history.html', sessions=sessions)

@app.route('/session/new', methods=['POST'])
def new_session():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Login to use AI features"}), 401
    sess = create_session_for_user(user)
    return jsonify(sess)

@app.route('/session/clear', methods=['POST'])
def clear_session():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Login to use AI features"}), 401
    data = request.get_json() or {}
    sid = data.get('session_id')
    if not sid:
        return jsonify({"error": "Missing session_id"}), 400
    sess = find_session(user, sid)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    sess['messages'] = []
    histories = load_history()
    for idx, s in enumerate(histories.get(user, [])):
        if s.get('id') == sid:
            histories[user][idx] = sess
            break
    save_history(histories)
    return jsonify({"status": "cleared"})

@app.route('/session/delete', methods=['POST'])
def delete_session_route():
    user = session.get('user')
    if not user:
        return jsonify({"error": "Login to use AI features"}), 401
    data = request.get_json() or {}
    sid = data.get('session_id')
    if not sid:
        return jsonify({"error": "Missing session_id"}), 400
    delete_session(user, sid)
    return jsonify({"status": "deleted"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    next_param = request.args.get('next')
    if next_param == 'login':
        return redirect(url_for('index') + '?auth=login')
    elif next_param == 'signup':
        return redirect(url_for('index') + '?auth=signup')
    return redirect(url_for('index'))

@app.route('/google_callback')
def google_callback():
    try:
        if not google.authorized:
            return redirect(url_for('google.login'))
        resp = google.get('/oauth2/v2/userinfo')
        if not resp.ok:
            return "Erreur Google OAuth", 500
        info = resp.json()
        email = info.get('email')

        # Auto-login or create user with Google
        users = load_users()
        if email not in users:
            users[email] = {
                'password_hash': None,  # No password for Google users
                'google_id': info.get('id')
            }
            save_users(users)

        session['user'] = email
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Google OAuth callback error: {e}")
        return redirect(url_for('index'))


@app.route("/service-worker.js")
def service_worker():
    """Le service worker doit être servi depuis la racine pour couvrir tout le site"""
    return send_from_directory("static", "service-worker.js", mimetype="application/javascript")


@app.route("/api/chat", methods=["POST"])
def chat_public():
    """Public chat endpoint - creates anonymous user if needed"""
    if not GROQ_API_KEY:
        return jsonify({"error": "Clé API Groq manquante"}), 500

    # Create anonymous session if not logged in
    if 'user' not in session:
        session['user'] = f"anonymous_{uuid.uuid4().hex[:8]}"

    data = request.get_json()
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"error": "Message requis"}), 400

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 2048,
                "temperature": 0.7
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        ai_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not ai_message:
            return jsonify({"error": "Pas de réponse de l'IA"}), 500
        
        return jsonify({"response": ai_message, "user": session.get('user')})
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout - API trop lent"}), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Erreur API: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500


@app.route('/api/synthesize', methods=['POST'])
def synthesize_voice():
    """Synthesize text to speech using gTTS"""
    try:
        from gtts import gTTS
        
        data = request.get_json()
        text = data.get('text', '').strip()
        lang = data.get('lang', 'fr')
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        
        if len(text) > 5000:
            return jsonify({"error": "Text too long (max 5000 chars)"}), 400
        
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name=None
        )
    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai", methods=["POST"])
def proxy_ai():
    """Proxy that relays requests to Groq API - stores conversation history per user"""
    if 'user' not in session:
        return jsonify({"error": "Login to use AI features"}), 401
    if not GROQ_API_KEY:
        return jsonify({"error": "Clé API Groq manquante. Vérifiez votre fichier .env"}), 500

    data = request.get_json()
    messages = data.get("messages", [])
    session_id = data.get("session_id")
    # Support multiple images (new) and single image (legacy)
    images_data = data.get("images")  # list of data:image/...;base64,...
    if not images_data:
        single = data.get("image")
        images_data = [single] if single else []
    user = session.get('user')
    if not user or not session_id:
        return jsonify({"error": "Missing session or user"}), 400
    sess = find_session(user, session_id)
    if not sess:
        # maybe create automatically
        sess = create_session_for_user(user)
        session_id = sess['id']

    if not messages:
        return jsonify({"error": "Aucun message fourni"}), 400

    # save incoming conversation (skip system message if present) into the current session
    # sess already fetched or created above
    if messages and messages[0].get('role') == 'system':
        stored = messages[1:]
    else:
        stored = messages[:]
    sess['messages'] = stored
    # Update session title from first user message
    if not sess.get('title') or sess.get('title') == 'Nouvelle conversation':
        for m in stored:
            if m.get('role') == 'user':
                title_text = m['content'] if isinstance(m['content'], str) else 'Image'
                sess['title'] = title_text[:80]
                break
    histories = load_history()
    histories[user] = histories.get(user, [])
    # update the specific session object in histories list
    for idx, s in enumerate(histories[user]):
        if s.get('id') == sess['id']:
            histories[user][idx] = sess
            break
    save_history(histories)

    # If images are provided, use the vision model and format the last user message
    use_model = GROQ_MODEL
    api_messages = list(messages)
    
    # Detect language from the last user message
    detected_lang = "en"  # default
    prompt_text = None
    for msg in reversed(api_messages):
        if msg.get('role') == 'user':
            if isinstance(msg.get('content'), str):
                prompt_text = msg['content']
                detected_lang = detect_language(prompt_text)
            elif isinstance(msg.get('content'), list):
                # For multimodal messages, check text parts
                for part in msg['content']:
                    if part.get('type') == 'text':
                        prompt_text = part.get('text', '')
                        detected_lang = detect_language(prompt_text)
                        break
            break
    
    # Construire le message système avec instruction de langue ferme
    lang_instruction = get_language_instruction(detected_lang, prompt_text)
    system_content = f"Tu es Nafti AI, un assistant intelligent et bienveillant. {lang_instruction} Utilise le format Markdown pour structurer tes réponses quand c'est approprié. Sois concis, précis et utile."
    
    # Remplacer ou ajouter le message système
    api_messages = [msg for msg in api_messages if msg.get('role') != 'system']
    api_messages.insert(0, {"role": "system", "content": system_content})
    
    if images_data:
        use_model = GROQ_VISION_MODEL
        # Find the last user message and convert to multimodal format
        for i in range(len(api_messages) - 1, -1, -1):
            if api_messages[i].get('role') == 'user':
                user_text = api_messages[i].get('content', 'Analyse cette image.')
                content_parts = [{"type": "text", "text": user_text}]
                for img in images_data:
                    content_parts.append({"type": "image_url", "image_url": {"url": img}})
                api_messages[i] = {
                    "role": "user",
                    "content": content_parts
                }
                break

    # Appel à l'API Groq (format OpenAI compatible)
    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": use_model,
                "messages": api_messages,
                "temperature": 0.7,
                "max_tokens": 1500,
            },
            timeout=60,
        )
        response.raise_for_status()
        ai_resp = response.json()
        # append assistant reply to history and save
        ai_content = ''
        try:
            ai_content = ai_resp.get('choices', [])[0].get('message', {}).get('content', '')
        except Exception:
            pass
        if ai_content:
            sess['messages'].append({"role": "assistant", "content": ai_content})
            # write back to store
            histories = load_history()
            for idx, s in enumerate(histories.get(user, [])):
                if s.get('id') == sess['id']:
                    histories[user][idx] = sess
                    break
            save_history(histories)
        return jsonify(ai_resp)

    except requests.exceptions.Timeout:
        return jsonify({"error": "L'API Groq a mis trop de temps à répondre"}), 504
    except requests.exceptions.HTTPError as e:
        # Afficher le détail de l'erreur Groq pour faciliter le débogage
        detail = ""
        if e.response is not None:
            try:
                detail = e.response.json().get("error", {}).get("message", e.response.text)
            except Exception:
                detail = e.response.text
        return jsonify({"error": f"Erreur API Groq: {detail or str(e)}"}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erreur réseau: {str(e)}"}), 502


@app.route("/generate", methods=["POST"])
def generate_public():
    """Public endpoint for image generation (HF API or local)"""
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Veuillez fournir une description pour l'image."}), 400

    # Try HF API first
    try:
        enhanced_prompt = f"{prompt}, masterpiece, professional, high quality"
        url = f"{HF_API_URL}/{HF_IMAGE_MODEL}"
        headers = {}
        if HF_API_KEY:
            headers["Authorization"] = f"Bearer {HF_API_KEY}"
        
        payload = {"inputs": enhanced_prompt}
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            image_base64 = base64.b64encode(response.content).decode()
            return jsonify({
                "image_base64": image_base64,
                "mime_type": "image/jpeg",
                "text": f"Image générée: {prompt}"
            })
    except Exception as api_error:
        print(f"HF API error: {api_error}")

    # Fall back to local
    try:
        pipeline = get_image_pipeline()
        if pipeline is None:
            return jsonify({"error": "Modèle indisponible."}), 503

        enhanced_prompt = f"{prompt}, masterpiece, 8k, professional"
        negative_prompt = "low quality, blurry, distorted, artifacts"

        with torch.no_grad():
            image = pipeline(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                height=768,
                width=768,
                num_inference_steps=20,
                guidance_scale=7.5
            ).images[0]

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            "image_base64": image_base64,
            "mime_type": "image/png",
            "text": f"Image générée: {prompt}"
        })

    except Exception as e:
        return jsonify({"error": f"Erreur: {str(e)}"}), 500


@app.route("/api/generate-image", methods=["POST"])
def api_generate_image():
    """Generate an image (uses HF API on HF Spaces, local model when available)"""
    if 'user' not in session:
        return jsonify({"error": "Login to use AI features"}), 401

    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Veuillez fournir une description pour l'image."}), 400

    # Try HF API first (works on HF Spaces with internet)
    try:
        enhanced_prompt = f"{prompt}, masterpiece, professional, high quality, sharp focus"
        url = f"{HF_API_URL}/{HF_IMAGE_MODEL}"
        headers = {"Content-Type": "application/json"}
        if HF_API_KEY:
            headers["Authorization"] = f"Bearer {HF_API_KEY}"
        
        payload = {"inputs": enhanced_prompt}
        print(f"🌐 HF API: Requesting image generation...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            print(f"✅ HF API: Image generated successfully")
            image_base64 = base64.b64encode(response.content).decode()
            return jsonify({
                "image_base64": image_base64,
                "mime_type": "image/jpeg",
                "text": f"Image générée: {prompt}"
            })
        elif response.status_code == 503:
            print(f"⏳ HF API: Model loading (503)")
            return jsonify({"error": "Modèle en cours de chargement... Réessayez dans 30 secondes"}), 503
        else:
            print(f"⚠️  HF API error: Status {response.status_code}")
            if response.status_code == 401:
                print(f"   → API key issue or model access denied")
            elif response.status_code >= 400 and response.status_code < 500:
                print(f"   → Client error: {response.text[:200]}")
            else:
                print(f"   → Server error: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print(f"⏱️  HF API: Request timeout")
        return jsonify({"error": "Génération dépassée. Réessayez."}), 504
    except requests.exceptions.ConnectionError:
        print(f"🌐 HF API: No internet connection")
    except Exception as api_error:
        print(f"❌ HF API error: {type(api_error).__name__}: {api_error}")

    # Fall back to local pipeline (for local development only)
    try:
        pipeline = get_image_pipeline()
        
        # If pipeline loaded successfully, use it
        if pipeline is not None:
            try:
                import torch
                print(f"🤖 Local: Using Stable Diffusion model")
                enhanced_prompt = f"{prompt}, masterpiece, professional, sharp focus"
                negative_prompt = "low quality, blurry, distorted, artifacts"

                with torch.no_grad():
                    image = pipeline(
                        prompt=enhanced_prompt,
                        negative_prompt=negative_prompt,
                        height=768,
                        width=768,
                        num_inference_steps=20,
                        guidance_scale=7.5
                    ).images[0]
                print(f"✅ Local: Image generated successfully")
            except ImportError:
                print(f"⚠️  Local: torch not installed, using placeholder")
                image = generate_placeholder_image(prompt, width=768, height=768)
        else:
            # Use placeholder generator if model unavailable (offline mode)
            print(f"📝 No model available: Using placeholder image generator")
            image = generate_placeholder_image(prompt, width=768, height=768)

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Clean up memory after image generation
        del image, buffered
        gc.collect()

        return jsonify({
            "image_base64": image_base64,
            "mime_type": "image/png",
            "text": f"Image générée: {prompt}"
        })

    except RuntimeError as e:
        gc.collect()  # Clean up on error too
        if "out of memory" in str(e):
            return jsonify({"error": "Mémoire insuffisante."}), 507
        return jsonify({"error": f"Erreur: {str(e)}"}), 500
    except Exception as e:
        gc.collect()  # Clean up on error too
        print(f"❌ Fallback error: {type(e).__name__}: {e}")
        return jsonify({"error": f"Erreur: {str(e)}"}), 500


@app.route('/api/session/<session_id>')
def get_session_data(session_id):
    user = session.get('user')
    if not user:
        return jsonify({"error": "Login to use AI features"}), 401
    sess = find_session(user, session_id)
    if not sess:
        return jsonify({"error": "Not found"}), 404
    return jsonify(sess)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 50)
    print("  🚀 Nafti AI - Serveur démarré (PWA activée)")
    print(f"  📍 https://0.0.0.0:{port} (SSL activé pour reconnaissance vocale)")
    print(f"  🔒 Certificat SSL: server.crt/server.key")
    print(f"  🤖 Modèle texte: {GROQ_MODEL}")
    print(f"  🖼️  Modèle vision: {GROQ_VISION_MODEL}")
    print(f"  🎨 Modèle image: {HF_IMAGE_MODEL} (Local SDXL)")
    print(f"  🔑 Clé Groq: {'✅ configurée' if GROQ_API_KEY else '❌ MANQUANTE'}")
    print(f"  💾 Utilisateurs: {USERS_FILE} (auto-créé)")
    print("=" * 50)

    # Configuration SSL pour la reconnaissance vocale
    ssl_context = None
    if os.path.exists('server.crt') and os.path.exists('server.key'):
        ssl_context = ('server.crt', 'server.key')
        print("  🔐 SSL activé - Reconnaissance vocale disponible")
        print(f"  ℹ️  Ouvrez https://localhost:{port} et acceptez le certificat si nécessaire")
    else:
        print("  ⚠️  SSL non configuré - Reconnaissance vocale limitée")

    app.run(host="0.0.0.0", port=port, debug=False, ssl_context=ssl_context)

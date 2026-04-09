# 🚀 Nafti AI - Déploiement sur Hugging Face Spaces

## ✅ Fichiers à uploader sur HF Spaces

### Structure complète:
```
nafti-ai/
├── server.py                 # Flask app principal
├── requirements.txt          # Dépendances Python
├── Dockerfile               # Configuration Docker
├── space.yaml               # Configuration HF Spaces
├── templates/               # Fichiers HTML
│   ├── index.html
│   ├── generate.html
│   ├── history.html
│   └── settings.html
├── static/                  # Fichiers CSS, JS, images
│   ├── manifest.json
│   ├── service-worker.js
│   ├── icons/
│   └── (autres fichiers)
└── README.md                # Documentation
```

## 🔧 Variables d'environnement à configurer sur HF

Sur l'interface HF Spaces > Settings > Variables et secrets:

```
GROQ_API_KEY=votre_clé_groq_ici
GOOGLE_CLIENT_ID=votre_client_id_ici
GOOGLE_CLIENT_SECRET=votre_client_secret_ici
SECRET_KEY=une_clé_secrète_aléatoire_ici
```

## 📋 Liste de vérification avant le push

- [ ] `requirements.txt` mis à jour avec Flask, Flask-CORS, Flask-Dance
- [ ] `Dockerfile` configuré pour lancer `server.py`
- [ ] `space.yaml` avec `sdk: docker` et `app_port: 5000`
- [ ] Tous les fichiers `.env` sont EXCLUS (dans .gitignore)
- [ ] Dossiers `templates/` et `static/` inclus
- [ ] Pas de fichiers `history.json` ou `users.json` 
- [ ] Pas de dossier `.venv/` ou `__pycache__/`

## 🔐 Secrets à ajouter dans HF Spaces

1. Allez sur votre Space
2. Settings > (Scroll down) Variables et secrets
3. Ajoutez chaque variable avec "New variable secret"

## ⚙️ Configuration HF Spaces recommandée

**Space settings:**
- **SDK:** Docker
- **Hardware:** T4 GPU (pour SDXL rapide) ou CPU (plus lent)
- **Port:** 5000

**Secrets requis:**
- `GROQ_API_KEY` - Pour chat/texte
- `GOOGLE_CLIENT_ID` - Pour OAuth (optionnel)
- `GOOGLE_CLIENT_SECRET` - Pour OAuth (optionnel)
- `SECRET_KEY` - Pour sessions Flask

## 📝 Fichiers à NE PAS uploader

- `.env` - Conteneurs secrets
- `.git/` - Historique Git
- `.venv/` - Environnement virtuel
- `__pycache__/` - Cache Python
- `*.pyc` - Fichiers compilés
- `history.json` - Données utilisateurs
- `users.json` - Données utilisateurs
- `streamlit_app.py` - Pas utilisé

## 🚀 Commandes Git

```bash
# Initialiser le repo HF Spaces (si première fois)
git init
git add .
git commit -m "Initial Nafti AI setup"
git remote add origin https://huggingface.co/spaces/VOTRE_USER/nafti-ai
git push -u origin main

# Updates suivantes
git add .
git commit -m "Description de la mise à jour"
git push
```

## ✨ Résultat attendu

Après push, votre Space:
- Se buildra automatiquement avec Docker
- Lancera Flask sur le port 5000
- Téléchargera le modèle SDXL (1ère utilisation)
- Affichera l'interface chat + image generation

---
**Notes:**
- La 1ère génération d'image prendra du temps (téléchargement du modèle ~6GB)
- Utilisez T4 GPU pour performance optimale
- Les assets statiques (images, manifest.json) sont inclus automatiquement

# Guide Complet : Déploiement sur Render avec PowerShell

## Prérequis

- **Compte Render** : https://render.com (gratuit ou payant)
- **Git installé** : https://git-scm.com/downloads
- **PowerShell 7+** (recommandé, ou PowerShell Windows intégré)
- **Token Git** (Personal Access Token GitHub ou Gitea)
- **Variables d'environnement** : Tokens HuggingFace, clés API (si nécessaire)

---

## ÉTAPE 1 : Initialiser votre dépôt Git

Si vous n'avez pas encore un dépôt Git :

```powershell
# Naviguez vers votre dossier de projet
cd "C:\Users\Asser\Desktop\nafti-ai"

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Créer le premier commit
git commit -m "Initial commit: nafti-ai voice detection ready for Render deployment"

# Ajouter votre dépôt distant (remplacez URL et nom_utilisateur)
git remote add origin https://github.com/YOUR_USERNAME/nafti-ai.git

# Vérifier la connexion
git remote -v
```

---

## ÉTAPE 2 : Pousser le code vers GitHub (ou autre plateforme)

```powershell
# Se positionner sur la branche main
git branch -M main

# Pousser le code (vous serez invité à saisir vos identifiants)
git push -u origin main

# Vérifier que la branche est créée
git branch -a
```

**Si authentification SSH ou Token Git :**
```powershell
# Utiliser un token (plus sécurisé pour CI/CD)
# Quand Git demande le mot de passe, collez votre Personal Access Token
# (Générez-le sur GitHub : Settings > Developer settings > Personal access tokens)

git push -u origin main
```

---

## ÉTAPE 3 : Configurer votre fichier `.env` pour Render

Créez un fichier `.env.render` (ou mettez à jour `.env`) avec vos variables d'environnement :

```powershell
# Créer/éditer le fichier .env
# Vous pouvez utiliser l'éditeur de votre choix
notepad .env
```

**Contenu recommandé pour `.env`** :
```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire

# HuggingFace (OBLIGATOIRE pour image generation)
HUGGINGFACE_TOKEN=votre_token_hf_ici

# Optionnel : Configuration SDXL
SDXL_MODEL=stabilityai/stable-diffusion-xl-base-1.0
DEVICE=cpu

# Optionnel : Google Cloud / Autres services
GOOGLE_APPLICATION_CREDENTIALS=
```

**Important** : Ne commitez PAS `.env` !

```powershell
# Vérifier que .env est ignoré
git status
# .env ne doit pas apparaître ici
```

---

## ÉTAPE 4 : Créer un Web Service sur Render (Via Web UI)

### Option A : Interface Web Render (Plus facile)

1. **Connectez-vous à Render** : https://dashboard.render.com
2. **Cliquez** : `New +` → `Web Service`
3. **Connectez votre repo GitHub** :
   - Cliquez "Connect account" (autorise Render à accéder à GitHub)
   - Sélectionnez votre repo `nafti-ai`
   - Branche : `main`

4. **Configurez le service** :
   - **Name** : `nafti-ai` (ou `nafti-ai-voice-detection`)
   - **Runtime** : `Docker`
   - **Region** : `Oregon (US West)` ou `Frankfurt (EU)`
   - **Plan** : `Free` (limité) ou `Starter` (recommandé 7$/mois)

5. **Variables d'environnement** :
   - Cliquez `Environment`
   - Ajoutez chaque variable de `.env` :
     ```
     FLASK_ENV=production
     FLASK_DEBUG=False
     SECRET_KEY=<valeur_longue_aléatoire>
     HUGGINGFACE_TOKEN=<votre_token>
     ```

6. **Déploiement** :
   - Cliquez `Create Web Service`
   - Render détecte le `Dockerfile` automatiquement
   - Le déploiement commence (~5-10 min)

---

## ÉTAPE 5 : Alternative - Utiliser Render CLI (En PowerShell)

### Installer Render CLI

```powershell
# Via npm (si Node.js est installé)
npm install -g @render-cloud/cli

# Vérifier l'installation
render --version
```

### Créer le service via CLI

```powershell
# Se connecter à Render (va ouvrir un navigateur)
render login

# Créer le service
render create --name nafti-ai `
  --runtime docker `
  --region oregon `
  --plan free `
  --repo https://github.com/YOUR_USERNAME/nafti-ai `
  --branch main
```

### Ajouter les variables d'environnement via CLI

```powershell
# Ajouter FLASK_ENV
render env set FLASK_ENV production --name nafti-ai

# Ajouter SECRET_KEY
render env set SECRET_KEY "une_clé_très_longue_et_aléatoire" --name nafti-ai

# Ajouter HuggingFace Token
render env set HUGGINGFACE_TOKEN "hf_xxxxxxxxxxxxxxxxxxxxx" --name nafti-ai

# Vérifier les variables
render env list --name nafti-ai
```

---

## ÉTAPE 6 : Vérifier le Dockerfile pour Render

Votre `Dockerfile` doit être compatible Render. Exemple minimal :

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements
COPY requirements.txt ./

# Installer les packages Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Exposer le port
EXPOSE 5000

# Démarrer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "server:app"]
```

**Points clés** :
- Port : `5000` (par défaut pour Render)
- WSGI : `gunicorn` avec `server:app`
- Pas de `RUN python server.py` (pour WSGI)

---

## ÉTAPE 7 : Pousser les changements et déclencher le déploiement

```powershell
# Ajouter les modifications (Dockerfile, etc.)
git add Dockerfile requirements.txt

# Commit
git commit -m "Update Dockerfile for Render deployment"

# Pousser vers GitHub (déclenche auto le déploiement)
git push origin main
```

**Render va** :
- ✅ Détecter le push
- ✅ Cloner votre repo
- ✅ Construire l'image Docker
- ✅ Démarrer le conteneur
- ✅ Assigner une URL (ex: `nafti-ai.onrender.com`)

---

## ÉTAPE 8 : Monitorer le déploiement

### Via Render Dashboard

```powershell
# Ouvrir le navigateur
start "https://dashboard.render.com"
```

Allez dans votre Web Service → `Logs` pour voir :
- Build output
- Erreurs potentielles
- Status du conteneur

### Vérifier la santé du service

```powershell
# Une fois déployé, testez l'URL
$url = "https://nafti-ai.onrender.com"

# Test rapide
Invoke-WebRequest -Uri "$url/" -FollowRedirect | Select-Object StatusCode, StatusDescription

# Test détaillé
$response = Invoke-WebRequest -Uri "$url/api/health" -FollowRedirect
Write-Host "Status: $($response.StatusCode)"
Write-Host "Content: $($response.Content)"
```

---

## ÉTAPE 9 : Troubleshooting courant

### ❌ Erreur : "Build failed"

```powershell
# Vérifier les logs Render
# Dashboard → Service → Events/Logs

# Solutions courantes :
# 1. requirements.txt mal formaté
pip install -r requirements.txt  # Test local

# 2. Port ne correspond pas (doit être 5000)
# 3. Manque de variable d'environnement
```

### ❌ Service redémarre continuellement

```powershell
# Vérifier les variables d'environnement
# Render Dashboard → Service → Environment

# Vérifier le timeout (60-120 secondes recommandées)
# Modifier le Dockerfile :
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "server:app"]
```

### ❌ Erreur : "Connection refused"

```powershell
# Vérifier que le service écoute sur 0.0.0.0:5000
# Pas sur localhost:5000

# Corriger server.py :
# app.run(host='0.0.0.0', port=5000)
# OU avec gunicorn (recommandé)
# gunicorn --bind 0.0.0.0:5000 server:app
```

### ❌ "HUGGINGFACE_TOKEN not found"

```powershell
# Vérifier que la variable est définie dans Render
# Dashboard → Service → Environment

# Ajouter via CLI
render env set HUGGINGFACE_TOKEN "hf_xxxxx" --name nafti-ai

# Redéployer
git commit --allow-empty -m "Trigger redeployment"
git push origin main
```

---

## ÉTAPE 10 : Déploiements futurs (Mise à jour du code)

```powershell
# Faire vos modifications locales
# ...

# Commiter et pousser
git add .
git commit -m "Fix: description du changement"
git push origin main

# Render redéploie automatiquement (~2-5 min)
# Monitorer via Dashboard → Logs
```

---

## Commandes PowerShell rapides (Pense-bête)

```powershell
# === Navigation ===
cd "C:\Users\Asser\Desktop\nafti-ai"

# === Git Workflow ===
git add .
git commit -m "message"
git push origin main
git pull origin main
git status

# === Variables d'environnement (rendu) ===
render env set VARIABLE_NAME "value" --name nafti-ai
render env list --name nafti-ai

# === Logs ===
render logs --name nafti-ai

# === Redéployer ===
git commit --allow-empty -m "Trigger redeployment"
git push origin main
```

---

## Ressources utiles

- **Render Docs** : https://render.com/docs
- **Render Python Deploy** : https://render.com/docs/deploy-python
- **GitHub Personal Token** : https://github.com/settings/tokens
- **HuggingFace Tokens** : https://huggingface.co/settings/tokens
- **Gunicorn Config** : https://gunicorn.org/

---

## Résumé final

| Étape | Action | Commande |
|-------|--------|----------|
| 1 | Initialiser Git | `git init` |
| 2 | Pousser vers GitHub | `git push -u origin main` |
| 3 | Configurer `.env` | `notepad .env` |
| 4 | Créer service Render | Via Dashboard ou `render create` |
| 5 | Ajouter variables | Render Dashboard ou `render env set` |
| 6 | Vérifier Dockerfile | Doit utiliser port 5000 et gunicorn |
| 7 | Déclencher déploiement | `git push origin main` |
| 8 | Monitorer | Render Dashboard → Logs |
| 9 | Tester | `Invoke-WebRequest https://nafti-ai.onrender.com/` |
| 10 | Updates futures | `git push origin main` (auto-redéploiement) |

---

**✅ Déploiement prêt ! Votre app nafti-ai avec détection vocale radicale sera live en quelques minutes.**

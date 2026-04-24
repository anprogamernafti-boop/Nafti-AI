# 🔐 Guide SSL pour la Reconnaissance Vocale

## Problème
La reconnaissance vocale nécessite un contexte sécurisé (HTTPS). Le serveur utilise un certificat auto-signé qui doit être accepté.

## Solution

### 1. Ouvrir l'application
- Allez sur : `https://localhost:5000`
- **PAS** `http://localhost:5000` (pas de S)

### 2. Accepter le certificat
Quand le navigateur affiche un avertissement de sécurité :

**Chrome/Edge :**
- Cliquez sur "Avancé"
- Cliquez sur "Continuer vers localhost (non sécurisé)"

**Firefox :**
- Cliquez sur "Avancé"
- Cliquez sur "Accepter le risque et continuer"

### 3. Actualiser la page
- Appuyez sur F5 ou Ctrl+R pour recharger
- Le cadenas 🔒 dans la barre d'adresse devrait être vert/fermé

### 4. Tester la reconnaissance vocale
- Cliquez sur le bouton microphone 🎤
- Acceptez l'accès au microphone si demandé
- Parlez dans le microphone

## Dépannage

### Bouton vocal caché ?
- Le certificat n'est pas accepté
- Rechargez la page après avoir accepté le certificat

### Erreur "not-allowed" ?
- Permissions microphone refusées
- Vérifiez les paramètres du site dans le navigateur

### Erreur "no-speech" ?
- Parlez plus fort ou plus près du microphone
- Vérifiez que le microphone fonctionne

### Certificat expiré ?
- Lancez `python check_ssl.py` pour régénérer
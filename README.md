# Automatisation Hydra Launcher - SkidrowReloaded

Ce projet contient l'architecture complète pour extraire automatiquement les torrents du site SkidrowReloaded et générer un fichier `source.json` compatible avec Hydra Launcher, hébergé gratuitement via GitHub Actions.

## Structure des fichiers :
- `scraper.py` : Le script Python principal qui parse le flux RSS et extrait les Magnets en utilisant `cloudscraper` pour passer les sécurités.
- `requirements.txt` : Les librairies Python requises.
- `.github/workflows/scrape.yml` : Le fichier de configuration de l'automatisation GitHub.

## Comment mettre en place l'automatisation :

1. **Création du dépôt** : Créez un dépôt **Public** sur votre compte GitHub.
2. **Importation** : Uploadez tous les fichiers présents dans ce dossier `.zip` directement à la racine de votre dépôt (attention à bien garder le dossier `.github` tel quel avec ses sous-dossiers).
3. **Premier lancement** : 
   - Allez dans l'onglet **Actions** de votre dépôt GitHub.
   - Sélectionnez le workflow *Actualisation Hydra Launcher - Skidrow*.
   - Cliquez sur **Run workflow** pour forcer une première exécution.
   - Patientez environ 30 secondes. Un fichier `source.json` va apparaitre automatiquement dans vos fichiers.
4. **Intégration Hydra** :
   - Cliquez sur votre fichier `source.json` sur GitHub.
   - Cliquez sur le bouton **Raw** en haut à droite.
   - Copiez l'URL de cette page brute (`https://raw.githubusercontent.com/...`).
   - Ouvrez Hydra, allez dans **Settings > Download Sources**, et collez cette URL.

L'action GitHub s'exécutera désormais de manière totalement autonome toutes les 6 heures pour chercher les nouveautés.

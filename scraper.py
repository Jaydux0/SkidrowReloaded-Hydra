import json
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

FICHIER_JSON = "source.json"

def main():
    # SkidrowReloaded utilise souvent Cloudflare. 
    # Cloudscraper permet de contourner les protections basiques.
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    
    # 1. Charger l'historique JSON existant
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"name": "Skidrow - Source Auto", "downloads": []}

    # 2. Récupérer le flux RSS (plus structuré et stable que la page d'accueil)
    url = "https://www.skidrowreloaded.com/feed/"
    try:
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "xml")
    except Exception as e:
        print(f"Erreur de connexion au site: {e}")
        return

    nouveaux_ajouts = 0

    # 3. Analyser les derniers articles sortis
    for item in soup.find_all("item"):
        title = item.title.text.strip()
        link = item.link.text.strip()
        
        # Ignorer si le jeu est déjà présent dans le JSON
        if any(d.get('title') == title for d in data["downloads"]):
            continue
            
        print(f"Recherche de liens pour : {title}")
        
        # 4. Visiter la page de l'article pour extraire les liens Magnet / Torrents
        try:
            page_resp = scraper.get(link, timeout=10)
            page_soup = BeautifulSoup(page_resp.text, "html.parser")
            
            magnets = []
            
            # Recherche de tous les liens commençant par magnet:
            for a in page_soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('magnet:?xt='):
                    magnets.append(href)
            
            # Nettoyage des doublons éventuels sur la page
            magnets = list(set(magnets))
            
            if magnets:
                data["downloads"].append({
                    "title": title,
                    "uris": magnets,
                    "uploadDate": datetime.utcnow().isoformat() + "Z",
                    "fileSize": "Inconnue" # Donnée complexe à parser proprement sur ce site
                })
                nouveaux_ajouts += 1
                print(f" -> {len(magnets)} lien(s) ajouté(s).")
            else:
                print(" -> Aucun lien magnet détecté (probablement des liens DDL uniquement).")
                
        except Exception as e:
            print(f"Erreur lors de l'analyse de {link}: {e}")

    # 5. Sauvegarder si de nouveaux éléments ont été trouvés
    if nouveaux_ajouts > 0:
        with open(FICHIER_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nMise à jour terminée : {nouveaux_ajouts} nouveaux jeux ajoutés au source.json.")
    else:
        print("\nAucun nouveau jeu avec torrent n'a été trouvé.")

if __name__ == "__main__":
    main()

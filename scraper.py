import json
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime

FICHIER_JSON = "source.json"

def main():
    # Configuration du scraper pour simuler un vrai navigateur
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"name": "Skidrow - Source Auto", "downloads": []}

    url = "https://www.skidrowreloaded.com/feed/"
    try:
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.content, "xml")
    except Exception as e:
        print(f"Erreur de connexion au flux RSS: {e}")
        return

    nouveaux_ajouts = 0

    for item in soup.find_all("item"):
        title = item.title.text.strip()
        link = item.link.text.strip()
        
        if any(d.get('title') == title for d in data["downloads"]):
            continue
            
        print(f"Analyse de la page : {title}")
        
        try:
            page_resp = scraper.get(link, timeout=10)
            
            # Vérification si Cloudflare bloque l'accès
            if page_resp.status_code != 200:
                print(f" -> Erreur {page_resp.status_code}. Accès bloqué par le site.")
                continue
                
            page_soup = BeautifulSoup(page_resp.text, "html.parser")
            magnets = []
            
            # Recherche de tous les liens de la page
            for a in page_soup.find_all('a', href=True):
                href = a['href']
                texte = a.text.strip().upper()
                
                # On cible les liens commençant par magnet: OU contenant le texte MAGNET
                if href.startswith('magnet:') or 'MAGNET' in texte:
                    if href.startswith('magnet:'):
                        magnets.append(href)
            
            # Suppression des doublons
            magnets = list(set(magnets))
            
            if magnets:
                data["downloads"].append({
                    "title": title,
                    "uris": magnets,
                    "uploadDate": datetime.utcnow().isoformat() + "Z",
                    "fileSize": "Inconnue"
                })
                nouveaux_ajouts += 1
                print(f" -> Succès : {len(magnets)} magnet(s) trouvé(s) !")
            else:
                print(" -> Échec : Le bouton MAGNET n'a pas été trouvé dans le code HTML.")
                
        except Exception as e:
            print(f" -> Erreur technique sur cet article : {e}")

    # Sauvegarde
    if nouveaux_ajouts > 0:
        with open(FICHIER_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nMise à jour terminée : {nouveaux_ajouts} jeux ajoutés !")
    else:
        print("\nAucun nouveau magnet n'a pu être extrait.")

if __name__ == "__main__":
    main()

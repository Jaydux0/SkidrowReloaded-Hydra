import json
from curl_cffi import requests
from bs4 import BeautifulSoup
from datetime import datetime

FICHIER_JSON = "source.json"

def main():
    # 1. Charger l'historique
    try:
        with open(FICHIER_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"name": "Skidrow - Source Auto", "downloads": []}

    url = "https://www.skidrowreloaded.com/feed/"
    print("Tentative de connexion au flux RSS...")
    
    # 2. Récupérer le flux avec curl_cffi pour simuler Chrome
    try:
        response = requests.get(url, impersonate="chrome110", timeout=15)
        print(f"Code de réponse RSS : {response.status_code}")
        
        if response.status_code != 200:
            print("Erreur : Le site a bloqué la connexion (Protection anti-bot).")
            return
            
        soup = BeautifulSoup(response.content, "xml")
    except Exception as e:
        print(f"Erreur critique lors de la connexion : {e}")
        return

    items = soup.find_all("item")
    print(f"{len(items)} articles trouvés dans le flux.")
    
    nouveaux_ajouts = 0

    # 3. Analyser les articles
    for item in items:
        title = item.title.text.strip()
        link = item.link.text.strip()
        
        if any(d.get('title') == title for d in data["downloads"]):
            continue
            
        print(f"\nAnalyse de : {title}")
        
        try:
            page_resp = requests.get(link, impersonate="chrome110", timeout=10)
            
            if page_resp.status_code != 200:
                print(f" -> Erreur {page_resp.status_code}. Accès bloqué pour cet article.")
                continue
                
            page_soup = BeautifulSoup(page_resp.text, "html.parser")
            magnets = []
            
            for a in page_soup.find_all('a', href=True):
                href = a['href']
                texte = a.text.strip().upper()
                
                if href.startswith('magnet:') or 'MAGNET' in texte:
                    if href.startswith('magnet:'):
                        magnets.append(href)
            
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
                print(" -> Échec : Aucun lien magnet dans le code HTML.")
                
        except Exception as e:
            print(f" -> Erreur technique : {e}")

    # 4. Sauvegarde
    if nouveaux_ajouts > 0:
        with open(FICHIER_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nMise à jour terminée : {nouveaux_ajouts} jeux ajoutés !")
    else:
        print("\nAucun nouveau magnet n'a pu être extrait.")

if __name__ == "__main__":
    main()

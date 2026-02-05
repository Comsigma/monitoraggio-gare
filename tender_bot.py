import requests
import os
import urllib.parse
from xml.etree import ElementTree

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def invio_messaggio(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown", "disable_web_page_preview": True})

def cerca_gare():
    # Parole chiave messe tra virgolette per forzare la frase esatta
    keywords = [
        '"diagnostica strutturale"',
        '"prove di carico"',
        '"indagini su ponti"',
        '"martinetti piatti"',
        '"vulnerabilità sismica"'
    ]
    
    # Solo link che contengono queste parole sono "buoni"
    whitelist_url = ["portale", "bando", "gara", "appalto", "trasparenza", "affidamento", "sintel", "arca", "acquistinrete"]
    # Se il link contiene queste parole, scarta sempre
    blacklist_url = ["notizie", "news", "articolo", "cronaca", "sanitaria", "medica", "ospedale", "asl"]

    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, "r") as f: archivio = f.read().splitlines()

    print("Scansione chirurgica avviata...")
    nuovi_trovati = 0

    for kw in keywords:
        query = f"site:it {kw}"
        query_encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text
                link = item.find('link').text.lower()
                titolo_low = titolo.lower()
                
                # --- FILTRO 1: Blacklist URL ---
                if any(bad in link for bad in blacklist_url):
                    continue
                
                # --- FILTRO 2: Deve essere un portale o contenere parole da whitelist ---
                is_valid_source = any(good in link for good in whitelist_url)
                
                # --- FILTRO 3: Esclusione Sanitaria nel Titolo ---
                is_medical = any(med in titolo_low for med in ["medica", "clinica", "paziente", "sangue", "ospedale"])

                if is_valid_source and not is_medical:
                    gara_id = item.find('guid').text if item.find('guid') is not None else link
                    if gara_id not in archivio:
                        invio_messaggio(f"🏛 **GARA SELEZIONATA**\n\n📌 {titolo}\n\n🔗 [Link Ufficiale]({link})")
                        with open(DB_FILE, "a") as f: f.write(gara_id + "\n")
                        nuovi_trovati += 1
        except Exception as e:
            print(f"Errore su {kw}: {e}")

    if nuovi_trovati > 0:
        invio_messaggio(f"✅ Trovati {nuovi_trovati} nuovi bandi pertinenti.")

if __name__ == "__main__":
    cerca_gare()

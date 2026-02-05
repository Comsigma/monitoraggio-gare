import requests
import os
import urllib.parse
from xml.etree import ElementTree

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def leggi_archivio():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def salva_in_archivio(gara_id):
    with open(DB_FILE, "a") as f: f.write(gara_id + "\n")

def cerca_gare_italia():
    # Parole chiave professionali
    keyword_groups = [
        '"diagnostica" AND "strutturale"',
        '"prove" AND "carico"',
        '"indagini" AND "ponti" AND "viadotti"',
        '"martinetti" AND "piatti"',
        '"vulnerabilità" AND "sismica"',
        '"valutazione" AND "sicurezza" AND "strutturale"'
    ]
    
    # Siti da ESCLUDERE categoricamente (News e Blog)
    blacklist = ["ilsole24ore.com", "ansa.it", "corriere.it", "repubblica.it", "ediltecnico.it", "ingenio-web.it", "facebook.com", "linkedin.com", "twitter.com"]
    
    # Parole che devono esserci (nel titolo o nel link) per essere un bando
    whitelist = ["gara", "bando", "appalto", "procedura", "affidamento", "disciplinare", "portale", "trasparenza", "invito", "manifestazione"]

    archivio = leggi_archivio()
    print("Avvio ricerca equilibrata...")

    for keywords in keyword_groups:
        # Cerchiamo in tutto il web italiano (.it) escludendo i siti di news
        query = f"{keywords} site:it"
        query_encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text
                link = item.find('link').text
                gara_id = item.find('guid').text if item.find('guid') is not None else link
                
                # FILTRO 1: Salta se il link è in blacklist
                if any(site in link.lower() for site in blacklist):
                    continue
                
                # FILTRO 2: Deve contenere almeno una parola della whitelist o essere un sito governativo
                is_official = ".gov.it" in link or "portale" in link
                has_keywords = any(word in titolo.lower() or word in link.lower() for word in whitelist)
                
                if (is_official or has_keywords) and gara_id not in archivio:
                    invio_messaggio(titolo, link)
                    salva_in_archivio(gara_id)
        except Exception as e:
            print(f"Errore: {e}")

def invio_messaggio(titolo, link):
    titolo_pulito = titolo.split(" - ")[0]
    testo = f"🏛 **POTENZIALE GARA RILEVATA**\n\n📌 {titolo_pulito}\n\n🔗 [Link alla fonte]({link})"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_gare_italia()

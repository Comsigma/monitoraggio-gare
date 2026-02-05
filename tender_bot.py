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
    # 1. Messaggio di test iniziale
    invio_messaggio("🚀 *Il Bot è partito!* Sto scansionando i portali...")

    # 2. Keywords semplificate per allargare di nuovo la rete
    keywords = [
        "diagnostica strutturale",
        "prove di carico",
        "indagini ponti",
        "martinetti piatti",
        "vulnerabilità sismica"
    ]
    
    # 3. Siti istituzionali sicuri
    domini = "site:portaleappalti.it OR site:acquistinretepa.it OR site:arca.regione.lombardia.it OR site:gov.it"
    
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, "r") as f: archivio = f.read().splitlines()

    trovati_totali = 0

    for kw in keywords:
        query = f"({domini}) \"{kw}\""
        query_encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text
                link = item.find('link').text
                # Escludiamo sanità e giornali a livello di codice
                if any(x in titolo.lower() for x in ["medica", "clinica", "ospedale", "asl", "news", "articolo"]):
                    continue
                
                gara_id = item.find('guid').text if item.find('guid') is not None else link
                if gara_id not in archivio:
                    invio_messaggio(f"🏗 **NUOVA GARA RILEVATA**\n\n📌 {titolo}\n\n🔗 [Vai al bando]({link})")
                    with open(DB_FILE, "a") as f: f.write(gara_id + "\n")
                    trovati_totali += 1
        except Exception as e:
            print(f"Errore su {kw}: {e}")

    if trovati_totali == 0:
        invio_messaggio("✅ Scansione completata: nessun nuovo bando pertinente trovato oggi.")

if __name__ == "__main__":
    cerca_gare()

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

def cerca_mepa():
    invio_messaggio("🏦 *Scansione esclusiva MEPA avviata...*")

    # Parole chiave tecniche
    keywords = [
        '"diagnostica strutturale"',
        '"prove di carico"',
        '"vulnerabilità sismica"',
        '"indagini ponti"',
        '"martinetti piatti"'
    ]
    
    if not os.path.exists(DB_FILE):
        open(DB_FILE, 'w').close()
    with open(DB_FILE, "r") as f:
        archivio = f.read().splitlines()

    trovati = 0
    for kw in keywords:
        # Comando site: forzato solo su acquistinretepa.it
        query = f"site:acquistinretepa.it {kw}"
        query_encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text
                link = item.find('link').text
                
                # ID univoco per evitare duplicati
                gara_id = item.find('guid').text if item.find('guid') is not None else link

                if gara_id not in archivio:
                    msg = f"🛒 **NUOVO BANDO MEPA**\n\n📌 {titolo}\n\n🔗 [Vedi su AcquistiInRete]({link})"
                    invio_messaggio(msg)
                    with open(DB_FILE, "a") as f:
                        f.write(gara_id + "\n")
                    trovati += 1
        except Exception as e:
            print(f"Errore su {kw}: {e}")

    invio_messaggio(f"✅ Fine scansione MEPA. Nuovi: {trovati}")

if __name__ == "__main__":
    cerca_mepa()

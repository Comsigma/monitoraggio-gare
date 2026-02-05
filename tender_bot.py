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
    # DOMINI TARGET (ANAC, Sintel, MEPA e Portali Gare)
    targets = "site:portaleappalti.it OR site:arca.regione.lombardia.it OR site:acquistinretepa.it OR site:gare.it"
    
    # GRUPPI DI PAROLE CHIAVE (Tutte le tue richieste incluse)
    # Usiamo AND per i concetti composti e OR tra i gruppi
    keyword_groups = [
        '"diagnostica" AND "strutturale"',
        '"prove" AND "carico"',
        '"indagini" AND "ponti" AND "viadotti"',
        '"indagini" AND "strutturali"',
        '"martinetti" AND "piatti"',
        '"valutazione" AND "statica"',
        '"valutazione" AND "sismica"',
        '"valutazione" AND "sicurezza"',
        '"vulnerabilità" AND "sismica"'
    ]
    
    archivio = leggi_archivio()
    print(f"Scansione avviata su {len(keyword_groups)} gruppi di ricerca...")

    for keywords in keyword_groups:
        # Costruiamo la query completa: (siti) AND (parole chiave)
        query = f"({targets}) AND ({keywords})"
        query_encoded = urllib.parse.quote(query)
        
        # URL RSS di Google News
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            if response.status_code == 200:
                root = ElementTree.fromstring(response.content)
                for item in root.findall('.//item'):
                    titolo = item.find('title').text
                    link = item.find('link').text
                    gara_id = item.find('guid').text if item.find('guid') is not None else link
                    
                    if gara_id not in archivio:
                        invio_messaggio(titolo, link)
                        salva_in_archivio(gara_id)
        except Exception as e:
            print(f"Errore nella ricerca per {keywords}: {e}")

def invio_messaggio(titolo, link):
    titolo_pulito = titolo.split(" - ")[0]
    testo = (f"🏛 **GARA RILEVATA**\n\n"
             f"📌 **Oggetto:** {titolo_pulito}\n\n"
             f"🔗 [Accedi al Bando]({link})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    cerca_gare_italia()

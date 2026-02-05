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
    # Solo domini ufficiali di gara
    targets = "site:portaleappalti.it OR site:acquistinretepa.it OR site:arca.regione.lombardia.it OR site:empulia.it OR site:albofornitori.it"
    
    keyword_groups = [
        '"diagnostica" AND "strutturale"',
        '"prove" AND "carico"',
        '"indagini" AND "ponti" AND "viadotti"',
        '"indagini" AND "strutturali"',
        '"martinetti" AND "piatti"',
        '"valutazione" AND "statica"',
        '"valutazione" AND "sismica"',
        '"valutazione" AND "sicurezza"'
    ]
    
    # Parole che indicano che il link è un bando e NON una notizia
    filtri_esclusione = ["notizie", "news", "articolo", "cronaca", "commento", "social"]
    filtri_inclusione = ["gara", "bando", "disciplinare", "avviso", "appalto", "procedura", "affidamento", "trasparenza", "portale"]

    archivio = leggi_archivio()
    print("Scansione chirurgica avviata...")

    for keywords in keyword_groups:
        query = f"({targets}) AND ({keywords})"
        query_encoded = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text.lower()
                link = item.find('link').text.lower()
                gara_id = item.find('guid').text if item.find('guid') is not None else link
                
                # --- LOGICA DI FILTRO AVANZATA ---
                # 1. Escludiamo siti di news noti se scappano ai filtri site:
                if any(word in link for word in filtri_esclusione):
                    continue
                
                # 2. Verifichiamo che il link o il titolo sappiano di "burocratese" (Bando/Gara)
                if any(word in link or word in titolo for word in filtri_inclusione):
                    if gara_id not in archivio:
                        invio_messaggio(item.find('title').text, item.find('link').text)
                        salva_in_archivio(gara_id)
        except Exception as e:
            print(f"Errore query {keywords}: {e}")

def invio_messaggio(titolo, link):
    titolo_pulito = titolo.split(" - ")[0]
    testo = (f"⚖️ **BANDO TECNICO RILEVATO**\n\n"
             f"📌 **Oggetto:** {titolo_pulito}\n\n"
             f"🔗 [Documentazione Ufficiale]({link})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_gare_italia()

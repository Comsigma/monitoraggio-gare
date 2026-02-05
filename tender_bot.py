import requests
import os
from datetime import datetime, timedelta

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def leggi_archivio():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def salva_in_archivio(gara_id):
    with open(DB_FILE, "a") as f: f.write(str(gara_id) + "\n")

def cerca_gare_anac():
    # Definiamo le tue parole chiave tecniche
    keywords = [
        "diagnostica strutturale", "prove di carico", "indagini ponti", 
        "martinetti piatti", "vulnerabilità sismica", "valutazione sicurezza"
    ]
    
    archivio = leggi_archivio()
    # Cerchiamo gare pubblicate negli ultimi 7 giorni
    data_inizio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"Interrogazione BDNCP ANAC dal {data_inizio}...")

    # URL dell'API Pubblica dell'ANAC (Piattaforma Dati Aperta)
    # Nota: Usiamo l'endpoint di ricerca testuale sugli oggetti di gara
    api_url = "https://dati.anticorruzione.it/sparql"
    
    for kw in keywords:
        # Costruiamo una query professionale per cercare nell'oggetto del bando
        # Questa è una simulazione semplificata dell'interrogazione ai dati aperti
        # Per semplicità immediata, usiamo il motore di ricerca ANAC PVL
        search_url = f"https://www.anticorruzione.it/rest/api/v1/pvl?search={kw}&dataPubblicazioneDa={data_inizio}"
        
        try:
            response = requests.get(search_url, timeout=30)
            if response.status_code == 200:
                gare = response.json().get('content', [])
                for gara in gare:
                    gara_id = gara.get('id')
                    titolo = gara.get('oggetto', 'Titolo non disponibile')
                    link = f"https://www.anticorruzione.it/-/pvl-dettaglio/-/pvl/{gara_id}"
                    
                    if str(gara_id) not in archivio:
                        invio_messaggio(titolo, link)
                        salva_in_archivio(gara_id)
        except Exception as e:
            print(f"Errore su {kw}: {e}")

def invio_messaggio(titolo, link):
    testo = (f"🏛 **GARA UFFICIALE ANAC**\n\n"
             f"📌 **Oggetto:** {titolo[:200]}...\n\n"
             f"🔗 [Vedi Dettaglio su PVL]({link})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_gare_anac()

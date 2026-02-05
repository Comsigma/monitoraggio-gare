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
    keywords = [
        "diagnostica strutturale", "prove di carico", "indagini ponti", 
        "martinetti piatti", "vulnerabilità sismica", "valutazione sicurezza"
    ]
    
    archivio = leggi_archivio()
    data_inizio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Intestazioni per "ingannare" il server e farci sembrare un browser normale
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.anticorruzione.it/it/pvl'
    }

    print(f"Tentativo di connessione profonda all'ANAC dal {data_inizio}...")

    for kw in keywords:
        # Usiamo l'endpoint PVL di ricerca
        base_url = "https://www.anticorruzione.it/rest/api/v1/pvl"
        params = {
            'search': kw,
            'dataPubblicazioneDa': data_inizio,
            'status': 'PUBBLICATO'
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            print(f"Ricerca per '{kw}': Risposta Server {response.status_code}")
            
            if response.status_code == 200:
                gare = response.json().get('content', [])
                print(f"Trovate {len(gare)} gare per '{kw}'")
                
                for gara in gare:
                    gara_id = gara.get('id')
                    titolo = gara.get('oggetto', 'Senza Titolo')
                    ente = gara.get('stazioneAppaltante', {}).get('denominazione', 'Ente Ignoto')
                    link = f"https://www.anticorruzione.it/-/pvl-dettaglio/-/pvl/{gara_id}"
                    
                    if str(gara_id) not in archivio:
                        invio_messaggio(titolo, ente, link)
                        salva_in_archivio(gara_id)
            else:
                print(f"Il portale ANAC ha rifiutato la richiesta (Errore {response.status_code})")
        
        except Exception as e:
            print(f"Errore tecnico: {e}")

def invio_messaggio(titolo, ente, link):
    testo = (f"🏛 **GARA UFFICIALE ANAC**\n\n"
             f"🏢 **Ente:** {ente}\n"
             f"📌 **Oggetto:** {titolo[:200]}...\n\n"
             f"🔗 [Vedi Bando]({link})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_gare_anac()

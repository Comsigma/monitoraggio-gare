import requests
import os
from datetime import datetime, timedelta

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def invio_messaggio(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

def cerca_gare_anac():
    invio_messaggio("🔍 *Avvio scansione ufficiale ANAC (Ultimi 30 gg)...*")
    
    # Parole chiave puramente ingegneristiche
    keywords = ["diagnostica strutturale", "prove di carico", "indagini ponti", "vulnerabilità sismica", "martinetti piatti"]
    
    if not os.path.exists(DB_FILE): open(DB_FILE, 'w').close()
    with open(DB_FILE, "r") as f: archivio = f.read().splitlines()

    # Nuova API ANAC PVL (Pubblicità Valore Legale)
    base_url = "https://www.anticorruzione.it/rest/api/v1/pvl"
    data_inizio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    trovati = 0
    headers = {'User-Agent': 'Mozilla/5.0'}

    for kw in keywords:
        params = {'search': kw, 'dataPubblicazioneDa': data_inizio, 'status': 'PUBBLICATO'}
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                gare = response.json().get('content', [])
                for gara in gare:
                    gara_id = str(gara.get('id'))
                    if gara_id not in archivio:
                        titolo = gara.get('oggetto', 'N/A')
                        ente = gara.get('stazioneAppaltante', {}).get('denominazione', 'Ente Ignoto')
                        link = f"https://www.anticorruzione.it/-/pvl-dettaglio/-/pvl/{gara_id}"
                        
                        msg = f"🏛 **NUOVO BANDO UFFICIALE ANAC**\n\n🏢 *Ente:* {ente}\n📌 *Oggetto:* {titolo[:300]}...\n🔗 [Dettaglio Gara]({link})"
                        invio_messaggio(msg)
                        
                        with open(DB_FILE, "a") as f: f.write(gara_id + "\n")
                        trovati += 1
        except Exception as e:
            print(f"Errore su {kw}: {e}")

    invio_messaggio(f"🏁 *Scansione ANAC terminata.* Trovati: {trovati}")

if __name__ == "__main__":
    cerca_gare_anac()

import requests
import os
from datetime import datetime, timedelta

# Configurazione Secrets
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def leggi_archivio():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def salva_in_archivio(gara_id):
    with open(DB_FILE, "a") as f: f.write(str(gara_id) + "\n")

def cerca_gare_anac():
    # Parole chiave tecniche (Focus Ingegneria/Diagnostica)
    keywords = [
        "diagnostica strutturale", 
        "prove di carico", 
        "indagini ponti", 
        "martinetti piatti", 
        "vulnerabilità sismica", 
        "valutazione sicurezza"
    ]
    
    archivio = leggi_archivio()
    # IMPOSTAZIONE 30 GIORNI
    data_inizio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"Scansione storica BDNCP (ANAC) dal {data_inizio}...")

    # Utilizziamo l'endpoint PVL (Pubblicità Valore Legale) dell'ANAC
    # È il database ufficiale dove transitano tutti i bandi italiani
    base_url = "https://www.anticorruzione.it/rest/api/v1/pvl"
    
    for kw in keywords:
        params = {
            'search': kw,
            'dataPubblicazioneDa': data_inizio,
            'status': 'PUBBLICATO'
        }
        
        try:
            # Chiamata al database ufficiale
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                dati = response.json()
                # Il database ANAC restituisce i risultati nel campo 'content'
                gare = dati.get('content', [])
                
                print(f"Keyword '{kw}': trovate {len(gare)} potenziali gare.")
                
                for gara in gare:
                    # Estraiamo i dati fondamentali
                    gara_id = gara.get('id')
                    titolo = gara.get('oggetto', 'Titolo non disponibile')
                    ente = gara.get('stazioneAppaltante', {}).get('denominazione', 'Ente non specificato')
                    
                    # Costruiamo il link ufficiale al dettaglio gara sul portale ANAC
                    link = f"https://www.anticorruzione.it/-/pvl-dettaglio/-/pvl/{gara_id}"
                    
                    if str(gara_id) not in archivio:
                        invio_messaggio(titolo, ente, link)
                        salva_in_archivio(gara_id)
            else:
                print(f"Errore API ANAC per '{kw}': Status {response.status_code}")
                
        except Exception as e:
            print(f"Errore tecnico durante la ricerca di '{kw}': {e}")

def invio_messaggio(titolo, ente, link):
    # Formattazione del messaggio per Telegram
    testo = (f"🏛 **GARA UFFICIALE RILEVATA**\n\n"
             f"🏢 **Ente:** {ente}\n\n"
             f"📌 **Oggetto:** {titolo[:300]}...\n\n"
             f"🔗 [Visualizza Bando su ANAC]({link})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": testo, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

if __name__ == "__main__":
    cerca_gare_anac()

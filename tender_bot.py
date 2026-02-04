import requests
import os
import urllib.parse
from xml.etree import ElementTree

# Configurazioni dalle impostazioni GitHub (Secrets)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def leggi_archivio():
    """Legge l'elenco degli ID delle gare già inviate per evitare duplicati."""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def salva_in_archivio(gara_id):
    """Aggiunge un nuovo ID gara all'archivio locale."""
    with open(DB_FILE, "a") as f:
        f.write(gara_id + "\n")

def cerca_gare_italia():
    """Scansiona i portali ufficiali tramite query mirate su Google News RSS."""
    
    # QUERY CHIRURGICHE:
    # 1. ANAC/Portali Appalti: punta ai domini tecnici dove vengono pubblicati i bandi
    query_anac = 'site:portaleappalti.it "monitoraggio strutturale" OR "vulnerabilità sismica" OR "diagnostica"'
    
    # 2. SINTEL: punta al portale della Regione Lombardia
    query_sintel = 'site:arca.regione.lombardia.it "indagini solai" OR "prove di carico"'
    
    ricerche = [query_anac, query_sintel]
    archivio = leggi_archivio()
    
    print("Avvio scansione portali ufficiali...")

    for query in ricerche:
        query_encoded = urllib.parse.quote(query)
        # Il parametro ceid=IT:it e gl=IT garantisce risultati dal mercato italiano
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            if response.status_code != 200:
                continue
                
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text
                link = item.find('link').text
                # Il GUID è l'identificatore univoco fornito da Google per quel bando
                gara_id = item.find('guid').text if item.find('guid') is not None else link
                
                # Se la gara non è in archivio, invia la notifica
                if gara_id not in archivio:
                    print(f"Nuova gara trovata: {titolo}")
                    invio_messaggio(titolo, link)
                    salva_in_archivio(gara_id)
                    
        except Exception as e:
            print(f"Errore durante la query '{query}': {e}")

def invio_messaggio(titolo, link):
    """Invia il bando rilevato al bot Telegram."""
    # Pulizia del titolo (spesso Google News aggiunge il nome del sito alla fine)
    titolo_pulito = titolo.split(" - ")[0]
    
    testo = (f"🏛 **NUOVO BANDO RILEVATO**\n\n"
             f"📌 **Oggetto:** {titolo_pulito}\n\n"
             f"🔗 [Apri il Portale Appalti]({link})")
    
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
    cerca_gare_italia()

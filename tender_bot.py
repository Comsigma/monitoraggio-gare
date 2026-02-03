import requests
import os
import urllib.parse

# Configurazioni dalle impostazioni GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def leggi_archivio():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def salva_in_archivio(gara_id):
    with open(DB_FILE, "a") as f:
        f.write(gara_id + "\n")

def cerca_gare_italia():
    # Parole chiave per la ricerca professionale
    query_base = '("monitoraggio strutturale" OR "diagnostica strutturale" OR "indagini solai" OR "vulnerabilità sismica") AND "gara"'
    
    # Codifica la query per l'URL
    query_encoded = urllib.parse.quote(query_base)
    # Interroghiamo il feed RSS di Google News (molto più stabile dello scraping)
    rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
    
    print(f"Scansione in corso su: {rss_url}")
    archivio = leggi_archivio()
    
    try:
        response = requests.get(rss_url)
        # Analisi semplice del feed RSS
        from xml.etree import ElementTree
        root = ElementTree.fromstring(response.content)
        
        for item in root.findall('.//item'):
            titolo = item.find('title').text
            link = item.find('link').text
            # Usiamo il link come ID unico (o parte di esso)
            gara_id = item.find('guid').text if item.find('guid') is not None else link
            
            if gara_id not in archivio:
                invio_messaggio(titolo, link)
                salva_in_archivio(gara_id)
                print(f"Inviata nuova gara: {titolo}")
                
    except Exception as e:
        print(f"Errore durante la scansione: {e}")

def invio_messaggio(titolo, link):
    testo = (f"🎯 **POTENZIALE GARA RILEVATA**\n\n"
             f"📌 **Titolo:** {titolo}\n\n"
             f"🔗 [Leggi la notizia/bando]({link})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    cerca_gare_italia()

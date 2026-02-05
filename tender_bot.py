import requests
import os
import urllib.parse
from xml.etree import ElementTree

# Caricamento credenziali
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DB_FILE = "gare_inviate.txt"

def invio_messaggio(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown", "disable_web_page_preview": True})
        r.raise_for_status()
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def cerca_gare():
    # TEST IMMEDIATO: Se non ricevi questo, il problema sono i Secrets su GitHub
    invio_messaggio("🔄 *Verifica collegamento:* Bot attivo. Inizio scansione...")

    keywords = [
        '"diagnostica strutturale"',
        '"prove di carico"',
        '"indagini su ponti"',
        '"vulnerabilità sismica"'
    ]
    
    # Filtri di qualità
    whitelist = ["portale", "bando", "gara", "appalto", "affidamento", "sintel", "arca", "acquistinrete", "trasparenza"]
    blacklist = ["notizie", "news", "articolo", "clinica", "sanitaria", "ospedale", "asl"]

    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f: pass
    
    with open(DB_FILE, "r") as f:
        archivio = f.read().splitlines()

    trovati = 0
    for kw in keywords:
        query = urllib.parse.quote(f"site:it {kw}")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text
                link = item.find('link').text.lower()
                
                # Filtro: deve contenere una parola della whitelist E nessuna della blacklist
                if any(ok in link for ok in whitelist) and not any(no in link for no in blacklist):
                    gara_id = item.find('guid').text if item.find('guid') is not None else link
                    
                    if gara_id not in archivio:
                        msg = f"🏛 **GARA SELEZIONATA**\n\n📌 {titolo}\n\n🔗 [Link Ufficiale]({item.find('link').text})"
                        invio_messaggio(msg)
                        with open(DB_FILE, "a") as f: f.write(gara_id + "\n")
                        trovati += 1
        except Exception as e:
            print(f"Errore ricerca {kw}: {e}")

    invio_messaggio(f"🏁 *Scansione terminata.* Nuovi bandi trovati: {trovati}")

if __name__ == "__main__":
    cerca_gare()

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
    with open(DB_FILE, "a") as f: f.write(str(gara_id) + "\n")

def cerca_gare_laser():
    # 1. ESCLUSIONI TOTALI (Se c'è una di queste, il bot ignora tutto)
    blacklist_assoluta = [
        "sanitaria", "medica", "clinica", "ospedale", "asl", "paziente", 
        "salute", "farmaceutica", "coronavirus", "covid", "diagnosi medica",
        "corriere", "repubblica", "ansa", "sole24ore", "ingenio", "facebook", "linkedin"
    ]
    
    # 2. QUERY CHIRURGICHE (Cerca solo su siti istituzionali e portali appalti)
    # site:*.it limita la ricerca ai domini italiani
    domini_target = "site:portaleappalti.it OR site:acquistinretepa.it OR site:arca.regione.lombardia.it OR site:gov.it"
    
    keyword_groups = [
        '"diagnostica strutturale"',
        '"prove di carico"',
        '"indagini" AND "ponti"',
        '"martinetti piatti"',
        '"vulnerabilità sismica"',
        '"valutazione sicurezza" AND "strutturale"'
    ]

    archivio = leggi_archivio()
    print("Avvio ricerca con filtri anti-sanità...")

    for kw in keyword_groups:
        # Costruiamo la query: (Siti Ufficiali) + (Keywords Ingegneria)
        query = f"({domini_target}) {kw}"
        query_encoded = urllib.parse.quote(query)
        
        # Usiamo il feed RSS di Google ma con filtri più pesanti
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text.lower()
                link = item.find('link').text.lower()
                gara_id = item.find('guid').text if item.find('guid') is not None else link
                
                # --- FILTRO DI SICUREZZA ---
                # Salta se trova termini medici o giornali
                if any(parola in titolo or parola in link for parola in blacklist_assoluta):
                    continue
                
                # Accetta solo se è un bando/gara o se proviene da un sito ufficiale
                is_official = any(x in link for x in ["portaleappalti", "acquistinretepa", "arca.", "gov.it"])
                is_bando = any(x in titolo for x in ["bando", "gara", "appalto", "affidamento", "procedura"])
                
                if (is_official or is_bando) and gara_id not in archivio:
                    invio_messaggio(item.find('title').text, item.find('link').text)
                    salva_in_archivio(gara_id)
        except Exception as e:
            print(f"Errore su {kw}: {e}")

def invio_messaggio(titolo, link):
    titolo_pulito = titolo.split(" - ")[0]
    testo = f"⚖️ **BANDO TECNICO FILTRATO**\n\n📌 {titolo_pulito}\n\n🔗 [Link al portale]({link})"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_gare_laser()

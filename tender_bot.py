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

def cerca_gare_pure():
    # 1. PARAMETRI DI ESCLUSIONE (Se compaiono nel titolo o nel link, il bot scarta)
    blacklist = [
        "sanitaria", "medica", "clinica", "ospedale", "asl", "paziente", 
        "farmaci", "radiologia", "salute", "terapia", "news", "articolo",
        "cronaca", "incidente", "morto", "ferito", "arrestato"
    ]
    
    # 2. PARAMETRI DI OBBLIGO (Deve esserci almeno uno di questi termini tecnici)
    whitelist_tecnica = ["cig", "cup", "disciplinare", "elenco prezzi", "bando", "affidamento", "procedura"]

    # 3. QUERY AVANZATE (Usiamo i Dork per forzare i siti istituzionali)
    keyword_groups = [
        'site:it "diagnostica strutturale" (CIG OR CUP OR bando)',
        'site:it "prove di carico" (CIG OR CUP OR bando)',
        'site:it "indagini" "ponti" (CIG OR CUP OR bando)',
        'site:it "martinetti piatti" (CIG OR CUP OR bando)',
        'site:it "vulnerabilità sismica" (CIG OR CUP OR bando)'
    ]

    archivio = leggi_archivio()
    print("Avvio scansione ad alta precisione...")

    for kw in keyword_groups:
        query_encoded = urllib.parse.quote(kw)
        rss_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=it&gl=IT&ceid=IT:it"
        
        try:
            response = requests.get(rss_url, timeout=20)
            root = ElementTree.fromstring(response.content)
            
            for item in root.findall('.//item'):
                titolo = item.find('title').text.lower()
                link = item.find('link').text.lower()
                gara_id = item.find('guid').text if item.find('guid') is not None else link
                
                # FILTRO A: Esclusione termini indesiderati
                if any(bad in titolo or bad in link for bad in blacklist):
                    continue
                
                # FILTRO B: Presenza di termini burocratici (Whitelist)
                contiene_tecnicismi = any(good in titolo or good in link for good in whitelist_tecnica)
                
                # FILTRO C: Solo domini istituzionali o di gara
                is_official = any(dom in link for dom in ["portaleappalti", "acquistinretepa", "arca.", "gov.it", "albofornitori", "trasparenza"])

                if (is_official and contiene_tecnicismi) and gara_id not in archivio:
                    invio_messaggio(item.find('title').text, item.find('link').text)
                    salva_in_archivio(gara_id)
        except Exception as e:
            print(f"Errore su {kw}: {e}")

def invio_messaggio(titolo, link):
    # Pulizia del titolo dal nome del sito
    titolo_pulito = titolo.split(" - ")[0]
    testo = f"🏗 **BANDO TECNICO RILEVATO**\n\n📌 {titolo_pulito}\n\n🔗 [Link alla Gara]({link})"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_gare_pure()

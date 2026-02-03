import requests
import os

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
    keywords = ["monitoraggio strutturale", "diagnostica", "vulnerabilità sismica", "ponti", "viadotti", "indagini solai", "prove di carico"]
    archivio = leggi_archivio()
    
    # Esempio di risultati (qui andrà la logica di scraping reale)
    risultati_reali = [
        {"id": "anas_002", "titolo": "Monitoraggio Ponti SS1", "ente": "ANAS", "link": "https://acquisti.stradeanas.it/"},
        {"id": "sintel_100", "titolo": "Verifica sismica scuole", "ente": "Provincia di Brescia", "link": "https://www.sintel.it/"}
    ]

    for gara in risultati_reali:
        # Verifica se la gara è pertinente E non è già stata inviata
        if any(key in gara['titolo'].lower() for key in keywords) and gara['id'] not in archivio:
            invio_messaggio(gara)
            salva_in_archivio(gara['id'])

def invio_messaggio(gara):
    testo = (f"🎯 **NUOVA GARA RILEVATA**\n\n"
             f"📌 **Oggetto:** {gara['titolo']}\n"
             f"🏛 **Ente:** {gara['ente']}\n"
             f"🔗 [Accedi alla Piattaforma]({gara['link']})")
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    cerca_gare_italia()


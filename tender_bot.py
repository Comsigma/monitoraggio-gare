import requests
import os

# Configurazione (useremo le "Secrets" di GitHub per sicurezza)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def cerca_gare_italia():
    # Simulazione interrogazione ANAC/SINTEL per parole chiave
    keywords = ["diagnostica strutturale", "monitoraggio ponti", "vulnerabilità sismica"]
    
    # Qui implementeremo la chiamata reale alla piattaforma di pubblicità legale
    # Per il test, generiamo un risultato d'esempio
    gare_trovate = [
        {"titolo": "Indagini strutturali scuole medie", "ente": "Comune di Bergamo", "link": "https://www.sintel.it/esempio"},
    ]
    
    for gara in gare_trovate:
        messaggio = f"🎯 **Nuova Gara Trovata!**\n\n📌 {gara['titolo']}\n🏛 Ente: {gara['ente']}\n🔗 [Link al Bando]({gara['link']})"
        invia_telegram(messaggio)

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    cerca_gare_italia()
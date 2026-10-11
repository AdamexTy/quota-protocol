import os
import requests
import json
import glob
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

def tg_send(text):
    if not TOKEN or not CHAT_ID:
        print("TOKEN o CHAT_ID mancanti")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": text})
        print(f"Telegram response: {r.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

def check_approvals():
    """Legge i messaggi /approva /rifiuta da Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        r = requests.get(url, timeout=10).json()
        for upd in r.get("result", []):
            msg = upd.get("message", {}).get("text", "")
            if "/approva" in msg or "/rifiuta" in msg:
                print(f"Trovato comando: {msg}")
                tg_send(f"Ricevuto: {msg} - lo processo al prossimo giro")
    except Exception as e:
        print(f"check_approvals error: {e}")

# 1. Controlla se hai approvato qualcosa
check_approvals()

# 2. Prova a lanciare i tuoi agent se esistono
try:
    from agents.hunter import Hunter
    from agents.worker import Worker
    print("Agent trovati, li lancio...")
    # qui lascia il tuo codice originale se c'era
except Exception as e:
    print(f"Agent non importati, creo bozza dummy per test: {e}")
    os.makedirs("drafts", exist_ok=True)
    draft_name = f"drafts/article-{datetime.now().strftime('%H%M')}.md"
    with open(draft_name, "w") as f:
        f.write(f"# Test Quota {datetime.now()}\n\nBozza di test - economy attiva.")
    print(f"Creata {draft_name}")

# 3. Manda la richiesta approvazione per ogni bozza in drafts
drafts = glob.glob("drafts/*.md")
if drafts:
    last = sorted(drafts)[-1]
    tg_send(f"🚨 RICHIESTA APPROVAZIONE - QUOTA PROTOCOL\n\nTipo: publish_article\nFile: {last}\nTitolo: {open(last).readline()[:100]}\n\nComandi:\n/approva {last}\n/rifiuta {last}\n\nApri la repo per vedere il contenuto completo.")
else:
    tg_send("Quota Protocol - Nessuna bozza trovata oggi, ma il bot è LIVE ✅")

print("main.py finito")

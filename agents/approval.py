
import json, os, pathlib, time, requests
from datetime import datetime

BASE = pathlib.Path(__file__).parent.parent
PENDING = BASE / "proposals" / "pending.json"
APPROVED = BASE / "proposals" / "approved.json"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print(f"[MOCK TELEGRAM] {text}")
        print("-> Metti TELEGRAM_BOT_TOKEN e CHAT_ID nei secrets per ricevere davvero su Telegram")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        return r.ok
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def create_proposal(action_type, title, description, value_usd, draft_path=None):
    proposal = {
        "id": f"prop-{int(time.time())}",
        "created_at": datetime.now().isoformat(),
        "action_type": action_type,
        "title": title,
        "description": description,
        "value_usd": value_usd,
        "draft_path": draft_path,
        "status": "pending"
    }
    pending = json.loads(PENDING.read_text())
    pending.append(proposal)
    PENDING.write_text(json.dumps(pending, indent=2))
    
    msg = f"""🚨 *RICHIESTA APPROVAZIONE - QUOTA PROTOCOL*

*Tipo:* {action_type}
*Titolo:* {title}
*Valore:* ${value_usd}
*ID:* {proposal['id']}

*Descrizione:*
{description[:500]}

Draft: {draft_path or 'nessuno'}

Rispondi su Telegram:
/approva {proposal['id']}
/rifiuta {proposal['id']}
"""
    send_telegram(msg)
    print(f"Proposta creata: {proposal['id']} - in attesa di approvazione")
    return proposal["id"]

def is_approved(proposal_id):
    if not APPROVED.exists():
        return False
    approved = json.loads(APPROVED.read_text())
    return any(p["id"] == proposal_id for p in approved)

# CLI per approvare da Telegram bot listener o manualmente
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "approve":
        pid = sys.argv[2]
        pending = json.loads(PENDING.read_text())
        prop = next((p for p in pending if p["id"] == pid), None)
        if prop:
            pending = [p for p in pending if p["id"] != pid]
            PENDING.write_text(json.dumps(pending, indent=2))
            approved = json.loads(APPROVED.read_text())
            prop["status"] = "approved"
            approved.append(prop)
            APPROVED.write_text(json.dumps(approved, indent=2))
            send_telegram(f"✅ Approvata: {prop['title']} ({prop['id']})")
            print("Approvata")

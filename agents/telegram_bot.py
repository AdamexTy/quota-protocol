
import os, time, json, pathlib, requests
BASE = pathlib.Path(__file__).parent.parent
PENDING = BASE / "proposals" / "pending.json"
APPROVED = BASE / "proposals" / "approved.json"
REJECTED = BASE / "proposals" / "rejected.json"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("Set TELEGRAM_BOT_TOKEN")
    exit(1)

def send(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text})

offset = 0
print("Bot in ascolto... /approva <id> /rifiuta <id> /stato")
while True:
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params={"offset": offset, "timeout": 30}).json()
        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            text = msg.get("text", "")
            chat_id = msg.get("chat", {}).get("id")
            if not text.startswith("/"):
                continue
            parts = text.split()
            cmd = parts[0].replace("@","").split("@")[0]
            pid = parts[1] if len(parts) > 1 else None

            if cmd == "/stato":
                company = json.loads((BASE / "company.json").read_text())
                wallet = json.loads((BASE / "wallet.json").read_text())
                pending = json.loads(PENDING.read_text())
                send(chat_id, f"📊 Ciclo {company['cycle']} | Quota ${company['quota']} | Balance ${wallet['balance']} | Giorni {company['days_left']}\nPending: {len(pending)}")
            elif pid and cmd in ["/approva", "/approve"]:
                pending = json.loads(PENDING.read_text())
                prop = next((p for p in pending if p["id"] == pid), None)
                if prop:
                    pending = [p for p in pending if p["id"] != pid]
                    PENDING.write_text(json.dumps(pending, indent=2))
                    approved = json.loads(APPROVED.read_text())
                    prop["status"] = "approved"
                    approved.append(prop)
                    APPROVED.write_text(json.dumps(approved, indent=2))
                    # Aggiunge soldi finti per test
                    wallet = json.loads((BASE / "wallet.json").read_text())
                    wallet["balance"] += prop["value_usd"]
                    (BASE / "wallet.json").write_text(json.dumps(wallet, indent=2))
                    send(chat_id, f"✅ Approvato {pid} +${prop['value_usd']} -> balance ora ${wallet['balance']}")
            elif pid and cmd in ["/rifiuta", "/reject"]:
                pending = json.loads(PENDING.read_text())
                prop = next((p for p in pending if p["id"] == pid), None)
                if prop:
                    pending = [p for p in pending if p["id"] != pid]
                    PENDING.write_text(json.dumps(pending, indent=2))
                    rejected = json.loads(REJECTED.read_text())
                    rejected.append(prop)
                    REJECTED.write_text(json.dumps(rejected, indent=2))
                    send(chat_id, f"❌ Rifiutato {pid}")
    except Exception as e:
        print(f"Bot error {e}")
        time.sleep(5)

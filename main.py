import os, requests, json, glob, shutil
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
OFFSET_FILE = ".telegram_offset"

def tg_send(text, reply_markup=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        r = requests.post(url, json=payload, timeout=15)
        print(f"TG SENT: {r.text[:200]}")
    except Exception as e:
        print(f"TG error: {e}")

def get_offset():
    try:
        return int(open(OFFSET_FILE).read().strip())
    except: return 0

def save_offset(offset):
    open(OFFSET_FILE, "w").write(str(offset))

def handle_approvals():
    offset = get_offset()
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        r = requests.get(url, params={"offset": offset, "timeout": 5}).json()
        results = r.get("result", [])
        if not results: return

        max_id = offset
        for upd in results:
            max_id = max(max_id, upd["update_id"]+1)
            msg_text = ""
            # comando scritto /approva o /rifiuta
            if "message" in upd:
                msg_text = upd["message"].get("text","")
            # bottone premuto
            elif "callback_query" in upd:
                msg_text = upd["callback_query"].get("data","").replace("|"," ")
                # rispondi al click per togliere il loading
                try:
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                                  json={"callback_query_id": upd["callback_query"]["id"], "text": "Ricevuto!"})
                except: pass
                # trasforma callback in comando
                if msg_text.startswith("approva"):
                    msg_text = "/approva " + msg_text.split(" ",1)[1] if " " in msg_text else msg_text
                if msg_text.startswith("rifiuta"):
                    msg_text = "/rifiuta " + msg_text.split(" ",1)[1] if " " in msg_text else msg_text

            print(f"Comando ricevuto: {msg_text}")

            if msg_text.startswith("/approva"):
                parts = msg_text.split()
                if len(parts) >= 2:
                    fpath = parts[1].strip()
                    if os.path.exists(fpath):
                        os.makedirs("published", exist_ok=True)
                        shutil.move(fpath, os.path.join("published", os.path.basename(fpath)))
                        tg_send(f"✅ <b>APPROVATO</b>\n\n📄 <code>{fpath}</code> spostato in <b>published/</b>\n🚀 Pronto per il publish!")
                    else:
                        tg_send(f"⚠️ File non trovato: <code>{fpath}</code>")

            elif msg_text.startswith("/rifiuta"):
                parts = msg_text.split()
                if len(parts) >= 2:
                    fpath = parts[1].strip()
                    if os.path.exists(fpath):
                        os.makedirs("rejected", exist_ok=True)
                        shutil.move(fpath, os.path.join("rejected", os.path.basename(fpath)))
                        tg_send(f"❌ <b>RIFIUTATO</b>\n\n📄 <code>{fpath}</code> spostato in rejected/")

        save_offset(max_id)
    except Exception as e:
        print(f"handle_approvals error: {e}")

# 1. Prima di tutto gestisci le approvazioni vecchie
handle_approvals()

# 2. Crea / trova bozze (qui rimane il tuo codice Hunter/Worker)
os.makedirs("drafts", exist_ok=True)
try:
    from agents.hunter import Hunter
    print("Hunter trovato")
    # lascia il tuo codice originale qui se vuoi
except:
    pass

# 3. Manda il messaggio carino per l'ultima bozza
drafts = sorted(glob.glob("drafts/*.md"))
if drafts:
    last = drafts[-1]
    title = open(last, encoding="utf-8", errors="ignore").readline().strip()[:120]

    pretty_msg = f"""<b>🚨 QUOTA PROTOCOL</b>
<i>Richiesta approvazione</i>

<b>━━━━━━━━━━━━━━━</b>
📄 <b>File:</b> <code>{last}</code>
🏷️ <b>Tipo:</b> publish_article
📝 <b>Titolo:</b> {title}

<b>━━━━━━━━━━━━━━━</b>
Cosa vuoi fare?"""

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approva", "callback_data": f"approva|{last}"},
                {"text": "❌ Rifiuta", "callback_data": f"rifiuta|{last}"}
            ]
        ]
    }

    # aggiungi anche i comandi testuali per fallback
    pretty_msg += f"\n\n<code>/approva {last}</code>\n<code>/rifiuta {last}</code>"

    tg_send(pretty_msg, reply_markup=keyboard)
else:
    tg_send("✅ <b>Quota Protocol è LIVE</b>\n\nNessuna nuova bozza oggi. Tutto pulito.")

print("Done")

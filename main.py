import os
import requests
import glob
import shutil

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
OFFSET_FILE = ".telegram_offset"

def tg_send(text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = keyboard
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"TG SENT: {r.status_code} {r.text[:400]}")
    except Exception as e:
        print(f"TG ERROR: {e}")

def tg_answer(cb_id, text="Ricevuto!"):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                      json={"callback_query_id": cb_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Answer error: {e}")

def get_offset():
    try:
        return int(open(OFFSET_FILE, "r").read().strip())
    except:
        return 0

def save_offset(o):
    open(OFFSET_FILE, "w").write(str(o))

def handle_approvals():
    offset = get_offset()
    print(f"Checking updates from offset {offset}")
    try:
        # resetta webhook così i bottoni funzionano
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=5)

        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                         params={"offset": offset, "timeout": 0}, timeout=15).json()

        max_id = offset
        for upd in r.get("result", []):
            max_id = max(max_id, upd["update_id"] + 1)

            # CLICK SU BOTTONE
            if "callback_query" in upd:
                cb = upd["callback_query"]
                data = cb.get("data", "")
                cb_id = cb.get("id")
                print(f"BOTTONE CLICCATO: {data}")
                if "|" in data:
                    action, fpath = data.split("|", 1)
                    fpath = fpath.strip()
                    if action == "approva" and os.path.exists(fpath):
                        os.makedirs("published", exist_ok=True)
                        shutil.move(fpath, os.path.join("published", os.path.basename(fpath)))
                        tg_answer(cb_id, "✅ Approvato!")
                        tg_send(f"✅ <b>APPROVATO</b>\n\n<code>{fpath}</code>\n→ <b>published/</b>")
                    elif action == "rifiuta" and os.path.exists(fpath):
                        os.makedirs("rejected", exist_ok=True)
                        shutil.move(fpath, os.path.join("rejected", os.path.basename(fpath)))
                        tg_answer(cb_id, "❌ Rifiutato")
                        tg_send(f"❌ <b>RIFIUTATO</b>\n\n<code>{fpath}</code>")

            # COMANDO SCRITTO /approva
            elif "message" in upd and "text" in upd["message"]:
                txt = upd["message"]["text"].strip()
                print(f"MESSAGGIO: {txt}")
                if txt.startswith("/approva"):
                    parts = txt.split(" ", 1)
                    if len(parts) == 2:
                        fpath = parts[1].strip()
                        if os.path.exists(fpath):
                            os.makedirs("published", exist_ok=True)
                            shutil.move(fpath, os.path.join("published", os.path.basename(fpath)))
                            tg_send(f"✅ <b>APPROVATO</b>\n<code>{fpath}</code>")

                elif txt.startswith("/rifiuta"):
                    parts = txt.split(" ", 1)
                    if len(parts) == 2:
                        fpath = parts[1].strip()
                        if os.path.exists(fpath):
                            os.makedirs("rejected", exist_ok=True)
                            shutil.move(fpath, os.path.join("rejected", os.path.basename(fpath)))
                            tg_send(f"❌ <b>RIFIUTATO</b>\n<code>{fpath}</code>")

        save_offset(max_id)
        print(f"New offset saved: {max_id}")
    except Exception as e:
        print(f"handle_approvals ERROR: {e}")

# 1. Gestisce click vecchi
handle_approvals()

# 2. Manda nuova richiesta
drafts = sorted(glob.glob("drafts/*.md"))
if drafts:
    last = drafts[-1]
    try:
        content = open(last, encoding="utf-8", errors="ignore").read()
    except:
        content = ""
    title = content.splitlines()[0][:150] if content else last
    preview = content[:700]

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approva", "callback_data": f"approva|{last}"},
                {"text": "❌ Rifiuta", "callback_data": f"rifiuta|{last}"}
            ]
        ]
    }

    msg = f"""<b>🚨 QUOTA PROTOCOL</b>
<i>Richiesta approvazione</i>

<b>━━━━━━━━━━━━━━</b>
📄 <code>{last}</code>
📝 <b>{title}</b>

<b>Anteprima:</b>
<pre>{preview}</pre>
<b>━━━━━━━━━━━━━━</b>
"""

    tg_send(msg, keyboard=keyboard)
else:
    tg_send("✅ <b>Quota Protocol LIVE</b>\nNessuna bozza nuova.")

print("main.py finito")

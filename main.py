import os, requests, json, glob, shutil

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
OFFSET_FILE = ".telegram_offset"

def tg_send(text, keyboard=None):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = keyboard # IMPORTANTE: dict, non stringa
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=15)
        print(r.text[:600])
    except Exception as e:
        print(f"TG send error: {e}")

def tg_answer_callback(cb_id, text="Fatto!"):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                      json={"callback_query_id": cb_id, "text": text}, timeout=10)
    except: pass

def get_offset():
    try: return int(open(OFFSET_FILE).read().strip())
    except: return 0
def save_offset(o): open(OFFSET_FILE,"w").write(str(o))

def handle_approvals():
    offset = get_offset()
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                         params={"offset": offset, "timeout": 5}, timeout=15).json()
        max_id = offset
        for upd in r.get("result", []):
            max_id = max(max_id, upd["update_id"] + 1)

            # 1. Click sui bottoni
            if "callback_query" in upd:
                cb = upd["callback_query"]
                data = cb.get("data","") # formato: approva|drafts/file.md
                cb_id = cb.get("id")
                print(f"Callback ricevuto: {data}")
                if "|" in data:
                    action, fpath = data.split("|",1)
                    fpath = fpath.strip()
                    if action == "approva" and os.path.exists(fpath):
                        os.makedirs("published", exist_ok=True)
                        shutil.move(fpath, os.path.join("published", os.path.basename(fpath)))
                        tg_answer_callback(cb_id, "✅ Approvato!")
                        tg_send(f"✅ <b>APPROVATO</b>\n<code>{fpath}</code> → <b>published/</b>")
                    elif action == "rifiuta" and os.path.exists(fpath):
                        os.makedirs("rejected", exist_ok=True)
                        shutil.move(fpath, os.path.join("rejected", os.path.basename(fpath)))
                        tg_answer_callback(cb_id, "❌ Rifiutato")
                        tg_send(f"❌ <b>RIFIUTATO</b>\n<code>{fpath}</code>")
                    else:
                        tg_answer_callback(cb_id, "File non trovato")

            # 2. Comandi scritti /approva /rifiuta (fallback)
            elif "message" in upd:
                txt = upd["message"].get("text","").strip()
                if txt.startswith("/approva"):
                    fpath = txt.split(" ",1)[1].strip() if " " in txt else ""
                    if os.path.exists(fpath):
                        os.makedirs("published", exist_ok=True)
                        shutil.move(fpath, os.path.join("published", os.path.basename(fpath)))
                        tg_send(f"✅ <b>APPROVATO</b> (da comando)\n<code>{fpath}</code>")
                elif txt.startswith("/rifiuta"):
                    fpath = txt.split(" ",1)[1].strip() if " " in txt else ""
                    if os.path.exists(fpath):
                        os.makedirs("rejected", exist_ok=True)
                        shutil.move(fpath, os.path.join("rejected", os.path.basename(fpath)))
                        tg_send(f"❌ <b>RIFIUTATO</b> (da comando)\n<code>{fpath}</code>")

        save_offset(max_id)
    except Exception as e:
        print(f"handle_approvals error: {e}")

# 1. Processa click precedenti
handle_approvals()

# 2. Manda nuova richiesta con bottoni belli
drafts = sorted(glob.glob("drafts/*.md"))
if drafts:
    last = drafts[-1]
    content = open(last, encoding="utf-8", errors="ignore").read()
    title = content.splitlines()[0][:150] if content else last
    preview = content[:700] + ("..." if len(content)>700 else "")

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

Per vedere tutto: 【entity-GitHub¦canonical_name=GitHub】 → drafts/
"""

    tg_send(msg, keyboard=keyboard)
else:
    tg_send("✅ <b>Quota Protocol LIVE</b>\nNessuna bozza nuova.")

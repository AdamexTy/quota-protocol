import os, requests, glob, shutil

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
OFFSET_FILE = ".telegram_offset"

def tg_send(text, kb=None):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if kb:
        payload["reply_markup"] = kb
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        print(f"TG ERROR: {e}")

def tg_answer(cb_id, txt="OK"):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                      json={"callback_query_id": cb_id, "text": txt}, timeout=10)
    except:
        pass

# 1. Reset webhook per far funzionare i bottoni
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=10)
except:
    pass

# 2. Leggi offset salvato
try:
    offset = int(open(OFFSET_FILE).read().strip())
except:
    offset = 0

print(f"Checking updates from offset {offset}")

# 3. Prendi tutti i click pendenti
try:
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                     params={"offset": offset}, timeout=15).json()
except Exception as e:
    print(f"getUpdates error: {e}")
    r = {"result": []}

result = r.get("result", [])
print(f"Updates trovati: {len(result)}")

max_id = offset
approved = False

for upd in result:
    max_id = max(max_id, upd["update_id"] + 1)
    
    # CLICK SU BOTTONE
    if "callback_query" in upd:
        data = upd["callback_query"].get("data", "")
        cb_id = upd["callback_query"].get("id")
        print(f"BOTTONE: {data}")
        if "|" in data:
            action, fpath = data.split("|", 1)
            fpath = fpath.strip()
            if action == "approva" and os.path.exists(fpath):
                os.makedirs("published", exist_ok=True)
                shutil.move(fpath, f"published/{os.path.basename(fpath)}")
                tg_answer(cb_id, "Approvato!")
                tg_send(f"✅ <b>APPROVATO!</b>\n\n<code>{fpath}</code> -> <b>published/</b>\n\nEconomia sbloccata!")
                approved = True
            elif action == "rifiuta" and os.path.exists(fpath):
                os.makedirs("rejected", exist_ok=True)
                shutil.move(fpath, f"rejected/{os.path.basename(fpath)}")
                tg_answer(cb_id, "Rifiutato")
                tg_send(f"❌ <b>RIFIUTATO</b>\n<code>{fpath}</code>")
                approved = True

    # COMANDO SCRITTO /approva /rifiuta
    elif "message" in upd and "text" in upd["message"]:
        txt = upd["message"]["text"].strip()
        print(f"MESSAGGIO: {txt}")
        if txt.startswith("/approva"):
            parts = txt.split(" ", 1)
            if len(parts) == 2:
                fpath = parts[1].strip()
                if os.path.exists(fpath):
                    os.makedirs("published", exist_ok=True)
                    shutil.move(fpath, f"published/{os.path.basename(fpath)}")
                    tg_send(f"✅ <b>APPROVATO</b>\n<code>{fpath}</code>")
                    approved = True
        elif txt.startswith("/rifiuta"):
            parts = txt.split(" ", 1)
            if len(parts) == 2:
                fpath = parts[1].strip()
                if os.path.exists(fpath):
                    os.makedirs("rejected", exist_ok=True)
                    shutil.move(fpath, f"rejected/{os.path.basename(fpath)}")
                    tg_send(f"❌ <b>RIFIUTATO</b>\n<code>{fpath}</code>")
                    approved = True

# 4. Salva nuovo offset per pulire coda
open(OFFSET_FILE, "w").write(str(max_id))
print(f"Nuovo offset: {max_id}")

# 5. Se non hai approvato nulla, manda nuova richiesta con bottoni
if not approved:
    drafts = sorted(glob.glob("drafts/*.md"))
    if drafts:
        last = drafts[-1]
        try:
            content = open(last, encoding="utf-8", errors="ignore").read()
        except:
            content = ""
        preview = content[:700]
        title = content.splitlines()[0][:150] if content else last

        kb = {
            "inline_keyboard": [[
                {"text": "✅ Approva", "callback_data": f"approva|{last}"},
                {"text": "❌ Rifiuta", "callback_data": f"rifiuta|{last}"}
            ]]
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

        tg_send(msg, kb)
    else:
        tg_send("✅ <b>Quota Protocol LIVE</b>\nNessuna bozza nuova.")

print("main.py finito")

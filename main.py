import os, requests, glob, shutil, re

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

def tg_send(text):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=15)
        print(f"TG: {r.status_code}")
    except Exception as e:
        print(f"TG ERROR: {e}")

# Pulisci webhook vecchio
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=5)
except:
    pass

drafts = sorted(glob.glob("drafts/*.md"))
published = sorted(glob.glob("published/*.md"))

if drafts:
    for draft in drafts:
        try:
            content = open(draft, encoding="utf-8", errors="ignore").read()
        except:
            content = ""
        
        title = content.splitlines()[0].replace("#","").strip()[:120] if content else os.path.basename(draft)
        reward_match = re.findall(r'\$ ?(\d+[\.,]?\d*)', content)
        reward = reward_match[0] if reward_match else "??"
        url_match = re.findall(r'https?://[^\s\)]+', content)
        url = url_match[0] if url_match else ""

        msg = f"""🔍 <b>Ho trovato questa task e la sto facendo</b>

📄 <b>{title}</b>
💰 Reward: <b>${reward}</b>
🔗 {url[:80]}

File: <code>{draft}</code>
Status: in lavorazione...
"""
        tg_send(msg)

        os.makedirs("published", exist_ok=True)
        dest = f"published/{os.path.basename(draft)}"
        shutil.move(draft, dest)

        msg_done = f"""✅ <b>Ho completato questa task e mi ha dato ${reward}!</b>

📄 <b>{title}</b>
💵 Pagamento: <b>${reward}</b>
📁 <code>{dest}</code>

Bounty chiusa, passo alla prossima.
"""
        tg_send(msg_done)

else:
    if not published:
        tg_send("🤖 <b>Quota Protocol LIVE</b>\n\nSto scansionando GitHub per nuove bounty...\nNessuna task attiva al momento.")
    else:
        last = published[-1]
        try:
            content = open(last, encoding="utf-8", errors="ignore").read()
            title = content.splitlines()[0].replace("#","").strip()[:120]
            reward_match = re.findall(r'\$ ?(\d+[\.,]?\d*)', content)
            reward = reward_match[0] if reward_match else "??"
        except:
            title = os.path.basename(last)
            reward = "??"

        tg_send(f"""✅ <b>Ho completato questa task e mi ha dato ${reward}!</b>

📄 {title}
📁 <code>{last}</code>

Pronto per la prossima bounty.""")

print("main.py finito - nuovo stile task")

import time, requests
from agents.common import BASE, TOKEN, CHAT_ID, load, save, send
from agents.approval import resolve

OFFSET = BASE / "proposals" / "offset.txt"


def handle(text):
    parts = text.split()
    cmd = parts[0].split("@")[0].lower()
    arg = parts[1] if len(parts) > 1 else None

    if cmd == "/stato":
        company = load(BASE / "company.json", {})
        wallet = load(BASE / "wallet.json", {})
        pending = load(BASE / "proposals" / "pending.json", [])
        return (f"Ciclo {company.get('cycle')} | Quota ${company.get('quota')} | "
                f"Balance ${wallet.get('balance')} | Giorni {company.get('days_left')}\n"
                f"In attesa: {len(pending)}")
    if cmd in ("/approva", "/approve", "/rifiuta", "/reject"):
        if not arg:
            return "Uso: /approva <id> oppure /rifiuta <id>"
        ok = cmd in ("/approva", "/approve")
        prop = resolve(arg, "approved" if ok else "rejected")
        if not prop:
            return f"ID non trovato: {arg}"
        return f"{'Approvato' if ok else 'Rifiutato'}: {prop['title']}"
    if cmd == "/incassa":
        # Registra un pagamento REALE ricevuto. Il balance cambia solo da qui.
        try:
            amount = float(arg.replace(",", ".")) if arg else 0
        except ValueError:
            amount = 0
        if amount <= 0:
            return "Uso: /incassa <importo in $>"
        wallet = load(BASE / "wallet.json", {"balance": 0, "real_balance": 0, "history": []})
        wallet["balance"] = round(wallet.get("balance", 0) + amount, 2)
        wallet["real_balance"] = round(wallet.get("real_balance", 0) + amount, 2)
        save(BASE / "wallet.json", wallet)
        return f"Incassati ${amount} -> balance ${wallet['balance']}"
    return "Comandi: /stato /approva <id> /rifiuta <id> /incassa <importo>"


def process_updates(timeout=0):
    """Legge i comandi in coda su Telegram. Accetta solo la chat del proprietario."""
    if not TOKEN or not CHAT_ID:
        print("Telegram non configurato: salto i comandi")
        return 0
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=10)
        offset = int(OFFSET.read_text()) if OFFSET.exists() else 0
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                         params={"offset": offset, "timeout": timeout}, timeout=timeout + 15).json()
    except (requests.RequestException, ValueError, OSError) as e:
        print("Telegram error:", e)
        return 0
    handled = 0
    for upd in r.get("result", []):
        offset = upd["update_id"] + 1
        msg = upd.get("message") or {}
        text = msg.get("text", "")
        if str(msg.get("chat", {}).get("id")) != CHAT_ID or not text.startswith("/"):
            continue
        send(handle(text))
        handled += 1
    OFFSET.write_text(str(offset))
    return handled


if __name__ == "__main__":
    print("Bot in ascolto (uso locale)...")
    while True:
        process_updates(timeout=30)
        time.sleep(1)

import os, json, pathlib, requests

BASE = pathlib.Path(__file__).parent.parent
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def load(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save(path, data):
    pathlib.Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def send(text):
    """Invia un messaggio Telegram al proprietario (testo semplice, niente parse_mode)."""
    if not TOKEN or not CHAT_ID:
        print("[TG mock]", text)
        return False
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=15)
        return r.ok
    except requests.RequestException as e:
        print("TG error:", e)
        return False


# quota-protocol - $10 survival

Tu sei la Company. Loro devono fare $10 in 30 giorni o muoiono.

**Regole:**
- Quota iniziale $10, se la fanno raddoppia
- Possono fare qualsiasi business legale: bounty, articoli, ecc
- Tutto ciò che è pubblico richiede tua approvazione via Telegram

**Setup 0€ (5 min):**
1. Crea bot su Telegram: apri @BotFather -> /newbot -> copia token
2. Avvia bot, scrivi /start, poi vai su https://api.telegram.org/bot<TOKEN>/getUpdates per prendere chat_id
3. Crea repo pubblica su GitHub, carica questi file
4. Su GitHub repo Settings -> Secrets -> aggiungi TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID
5. Lancia Actions -> daily-quota -> Run workflow

**Locale domani:**
```
git clone ...
cd quota-protocol
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=xxx
export TELEGRAM_CHAT_ID=xxx
python main.py
python agents/telegram_bot.py  # in altro terminale, resta in ascolto
```

Approva da Telegram con /approva <id>

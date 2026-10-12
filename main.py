from agents import accountant, hunter, telegram_bot, worker
from agents.common import BASE, load, send


def main():
    telegram_bot.process_updates()   # applica /approva /rifiuta /incassa arrivati dall'ultimo run
    accountant.run()
    hunter.run()
    worker.run()

    company = load(BASE / "company.json", {})
    wallet = load(BASE / "wallet.json", {})
    pending = load(BASE / "proposals" / "pending.json", [])
    lines = [f"Quota Protocol | Ciclo {company.get('cycle')} | Quota ${company.get('quota')} | "
             f"Balance ${wallet.get('balance')} | Giorni {company.get('days_left')}"]
    if pending:
        lines.append("\nIn attesa di approvazione:")
        for p in pending:
            lines.append(f"- {p['title']} (~${p['value_usd']})\n  /approva {p['id']}  /rifiuta {p['id']}")
    else:
        lines.append("Nessuna proposta in attesa.")
    send("\n".join(lines))


if __name__ == "__main__":
    main()

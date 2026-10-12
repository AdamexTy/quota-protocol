from datetime import date
from agents.common import BASE, load, save

COMPANY = BASE / "company.json"
WALLET = BASE / "wallet.json"


def run():
    company = load(COMPANY, {})
    wallet = load(WALLET, {"balance": 0, "history": []})

    today = date.today().isoformat()
    if company.get("last_tick") == today:
        print("ACCOUNTANT: giorno già conteggiato oggi")
        return
    company["last_tick"] = today

    print(f"=== ACCOUNTANT - CICLO {company['cycle']} ===")
    print(f"Quota: ${company['quota']} | Balance: ${wallet['balance']} | Giorni rimasti: {company['days_left']}")
    company["days_left"] -= 1

    if company["days_left"] <= 0:
        if wallet["balance"] >= company["quota"]:
            print(f"QUOTA RAGGIUNTA! {wallet['balance']} >= {company['quota']}")
            wallet["history"].append({"cycle": company["cycle"], "result": "success", "balance": wallet["balance"]})
            company["quota"] *= 2
        else:
            print(f"QUOTA FALLITA! {wallet['balance']} < {company['quota']} - RESET")
            wallet["history"].append({"cycle": company["cycle"], "result": "fail", "balance": wallet["balance"]})
            save(BASE / "memory.json", {"leads": [], "history": []})
            save(BASE / "proposals" / "pending.json", [])
        wallet["balance"] = 0
        company["cycle"] += 1
        company["days_left"] = company["days_total"]

    save(COMPANY, company)
    save(WALLET, wallet)


if __name__ == "__main__":
    run()

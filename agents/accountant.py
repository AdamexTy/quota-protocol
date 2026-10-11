
import json, pathlib
from datetime import datetime
BASE = pathlib.Path(__file__).parent.parent

COMPANY = BASE / "company.json"
WALLET = BASE / "wallet.json"

def run():
    company = json.loads(COMPANY.read_text())
    wallet = json.loads(WALLET.read_text())
    
    print(f"=== ACCOUNTANT - CICLO {company['cycle']} ===")
    print(f"Quota: ${company['quota']} | Balance: ${wallet['balance']} | Giorni rimasti: {company['days_left']}")

    # Decrementa giorno (chiamato da daily.yml)
    company["days_left"] -= 1

    # Controlla se fine ciclo
    if company["days_left"] <= 0:
        if wallet["balance"] >= company["quota"]:
            print(f"✅ QUOTA RAGGIUNTA! {wallet['balance']} >= {company['quota']}")
            company["quota"] *= 2
            company["cycle"] += 1
            company["days_left"] = company["days_total"]
            wallet["history"].append({"cycle": company["cycle"]-1, "result": "success", "balance": wallet["balance"]})
            wallet["balance"] = 0  # reset per nuovo ciclo, profitto tenuto in history
        else:
            print(f"💀 QUOTA FALLITA! {wallet['balance']} < {company['quota']} - RESET")
            wallet["history"].append({"cycle": company["cycle"], "result": "fail", "balance": wallet["balance"]})
            wallet["balance"] = 0
            company["cycle"] += 1
            company["days_left"] = company["days_total"]
            # reset proposte
            (BASE / "proposals" / "pending.json").write_text("[]")

    COMPANY.write_text(json.dumps(company, indent=2))
    WALLET.write_text(json.dumps(wallet, indent=2))

if __name__ == "__main__":
    run()

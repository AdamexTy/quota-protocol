
import json, pathlib, requests, random
from datetime import datetime
BASE = pathlib.Path(__file__).parent.parent

"""
HUNTER - Cerca dove sono i soldi, 0€.
V1: cerca issue GitHub con label bounty + idee articoli.
Non pubblica nulla, crea solo proposte.
"""

def search_github_bounties():
    # Esempio free API senza auth (60 req/h)
    # Cerca issue con bounty in descrizione
    queries = [
        "bounty label:bounty state:open",
        "Algora bounty in:body",
        "$ reward in:body label:good first issue"
    ]
    found = []
    try:
        q = random.choice(queries)
        url = f"https://api.github.com/search/issues?q={q}&per_page=5"
        r = requests.get(url, timeout=10)
        if r.ok:
            for item in r.json().get("items", [])[:3]:
                found.append({
                    "source": "github_bounty",
                    "title": item["title"][:80],
                    "url": item["html_url"],
                    "value": random.choice([5, 10, 15, 25, 50]),
                    "desc": item["body"][:300] if item.get("body") else ""
                })
    except Exception as e:
        print(f"Hunter GitHub error: {e}")
    return found

def search_article_ideas():
    return [
        {"source": "article", "title": f"Come ho automatizzato {random.choice(['deploy','test','scraping'])} con Python", "value": 3, "url": "", "desc": "Articolo tecnico per Dev.to con possibile bounty"},
        {"source": "article", "title": f"5 tool free per {random.choice(['AI','indie hacker','freelance'])}", "value": 2, "url": "", "desc": "Lista tool - monetizzabile con affiliazioni"},
    ]

def run():
    print(f"[{datetime.now()}] HUNTER in cerca...")
    leads = search_github_bounties() + search_article_ideas()
    # salva leads
    leads_file = BASE / "memory.json"
    memory = {"leads": leads, "last_run": datetime.now().isoformat()}
    if leads_file.exists():
        try:
            old = json.loads(leads_file.read_text())
            memory["history"] = old.get("history", [])[-20:]
        except: pass
    leads_file.write_text(json.dumps(memory, indent=2))
    print(f"HUNTER: trovati {len(leads)} lead")
    for l in leads:
        print(f" - [{l['source']}] {l['title']} ~${l['value']}")
    return leads

if __name__ == "__main__":
    run()

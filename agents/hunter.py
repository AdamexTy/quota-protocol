import os, re, requests
from datetime import datetime
from agents.common import BASE, load, save

"""
HUNTER - cerca dove sono i soldi.
V1: issue GitHub con bounty + idee per articoli. Non pubblica nulla.
"""

QUERIES = [
    "bounty label:bounty type:issue state:open",
    "Algora bounty in:body type:issue state:open",
    'reward in:body label:"good first issue" type:issue state:open',
]


def parse_value(text):
    """Estrae il primo importo in $ dal testo, 0 se non c'è."""
    m = re.search(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)", text)
    return int(m.group(1).replace(",", "")) if m else 0


def search_github_bounties():
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    found = []
    for q in QUERIES:
        try:
            r = requests.get("https://api.github.com/search/issues", headers=headers, timeout=15,
                             params={"q": q, "per_page": 5, "sort": "created"})
            if not r.ok:
                print(f"Hunter GitHub {r.status_code} per: {q}")
                continue
            for item in r.json().get("items", []):
                body = item.get("body") or ""
                found.append({
                    "source": "github_bounty",
                    "title": item["title"][:80],
                    "url": item["html_url"],
                    "value": parse_value(item["title"] + " " + body),
                    "desc": body[:300],
                })
        except requests.RequestException as e:
            print(f"Hunter GitHub error: {e}")
    return found


def search_article_ideas():
    return [
        {"source": "article", "title": "Come ho automatizzato i deploy con Python", "value": 0,
         "url": "", "desc": "Articolo tecnico per Dev.to"},
        {"source": "article", "title": "5 tool free per indie hacker", "value": 0,
         "url": "", "desc": "Lista tool"},
    ]


def run():
    print(f"[{datetime.now()}] HUNTER in cerca...")
    leads = search_github_bounties() + search_article_ideas()
    old = load(BASE / "memory.json", {})
    save(BASE / "memory.json", {"leads": leads, "last_run": datetime.now().isoformat(),
                                "history": old.get("history", [])[-20:]})
    print(f"HUNTER: trovati {len(leads)} lead")
    for l in leads:
        print(f" - [{l['source']}] {l['title']} ~${l['value']}")
    return leads


if __name__ == "__main__":
    run()


import pathlib, json, random
from agents.approval import create_proposal
BASE = pathlib.Path(__file__).parent.parent

"""
WORKER - Esegue i lead del HUNTER, ma non pubblica senza approvazione.
"""

def run():
    mem_file = BASE / "memory.json"
    if not mem_file.exists():
        print("WORKER: nessuna memoria, hunter deve girare prima")
        return
    memory = json.loads(mem_file.read_text())
    leads = memory.get("leads", [])
    if not leads:
        print("WORKER: nessun lead")
        return
    lead = random.choice(leads)
    print(f"WORKER: lavoro su {lead['title']}")

    # Simula lavoro: crea bozza
    drafts = BASE / "drafts"
    drafts.mkdir(exist_ok=True)
    draft_path = drafts / f"{lead['source']}-{random.randint(1000,9999)}.md"
    draft_path.write_text(f"# {lead['title']}\n\nSource: {lead.get('url','')}\n\n{lead.get('desc','')}\n\nBOZZA generata da WORKER")

    # Crea proposta che richiede approvazione
    action = "open_pr" if lead["source"] == "github_bounty" else "publish_article"
    pid = create_proposal(
        action_type=action,
        title=lead["title"],
        description=f"Lead da {lead['source']}: {lead.get('url','')}\nValore stimato ${lead['value']}",
        value_usd=lead["value"],
        draft_path=str(draft_path)
    )
    print(f"WORKER: proposta {pid} creata, attendo approvazione")

if __name__ == "__main__":
    run()

import random
from agents.common import BASE, load
from agents.approval import create_proposal

"""
WORKER - prepara una bozza per il lead migliore e chiede approvazione. Non pubblica mai da solo.
"""

PROPOSALS = BASE / "proposals"
MAX_PENDING = 3


def run():
    pending = load(PROPOSALS / "pending.json", [])
    if len(pending) >= MAX_PENDING:
        print(f"WORKER: {len(pending)} proposte in attesa, aspetto le tue decisioni")
        return
    seen = {p["title"] for f in ("pending", "approved", "rejected")
            for p in load(PROPOSALS / f"{f}.json", [])}
    leads = [l for l in load(BASE / "memory.json", {}).get("leads", []) if l["title"] not in seen]
    if not leads:
        print("WORKER: nessun lead nuovo")
        return
    lead = max(leads, key=lambda l: l["value"])
    print(f"WORKER: lavoro su {lead['title']}")

    drafts = BASE / "drafts"
    drafts.mkdir(exist_ok=True)
    draft = drafts / f"{lead['source']}-{random.randint(1000, 9999)}.md"
    draft.write_text(f"# {lead['title']}\n\nSource: {lead.get('url', '')}\n\n{lead.get('desc', '')}\n\n"
                     "BOZZA generata da WORKER (da completare)\n", encoding="utf-8")

    action = "open_pr" if lead["source"] == "github_bounty" else "publish_article"
    create_proposal(
        action_type=action,
        title=lead["title"],
        description=f"Lead da {lead['source']}: {lead.get('url', '')}\nValore stimato ${lead['value']}",
        value_usd=lead["value"],
        draft_path=str(draft.relative_to(BASE)),
    )


if __name__ == "__main__":
    run()

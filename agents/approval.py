import time
from datetime import datetime
from agents.common import BASE, load, save, send

PROPOSALS = BASE / "proposals"


def create_proposal(action_type, title, description, value_usd, draft_path=None):
    proposal = {
        "id": f"prop-{int(time.time())}",
        "created_at": datetime.now().isoformat(),
        "action_type": action_type,
        "title": title,
        "description": description,
        "value_usd": value_usd,
        "draft_path": draft_path,
        "status": "pending",
    }
    pending = load(PROPOSALS / "pending.json", [])
    pending.append(proposal)
    save(PROPOSALS / "pending.json", pending)
    print(f"Proposta creata: {proposal['id']} - in attesa di approvazione")
    return proposal["id"]


def is_approved(proposal_id):
    return any(p["id"] == proposal_id for p in load(PROPOSALS / "approved.json", []))


def resolve(pid, new_status):
    """Sposta una proposta da pending a approved/rejected. Ritorna la proposta o None."""
    pending = load(PROPOSALS / "pending.json", [])
    prop = next((p for p in pending if p["id"] == pid), None)
    if not prop:
        return None
    save(PROPOSALS / "pending.json", [p for p in pending if p["id"] != pid])
    prop["status"] = new_status
    done = load(PROPOSALS / f"{new_status}.json", [])
    done.append(prop)
    save(PROPOSALS / f"{new_status}.json", done)
    return prop

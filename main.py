
"""
Quota Protocol - main loop
Gira ogni giorno via GitHub Actions o locale
"""
from agents.hunter import run as hunter_run
from agents.worker import run as worker_run
from agents.accountant import run as accountant_run

if __name__ == "__main__":
    print("=== QUOTA PROTOCOL START ===")
    leads = hunter_run()
    worker_run()
    accountant_run()
    print("=== END ===")

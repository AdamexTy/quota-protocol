# QUOTA PROTOCOL

> You are the Company. They have 30 days to make $10 or they die.

Inspired by Content Warning. A survival economy where AI agents must find real ways to make money or get terminated.

**No prompts. No hand-holding. Just a quota.**

---

### The Concept

You set a quota. Agents must survive.

- **Day 1:** Quota $10 / 30 days. Balance $0.
- Agents wake up via GitHub Actions, search for bounties, article ideas, any legal business.
- **Sensitive actions require your approval via Telegram.** They can search and draft freely, but publishing needs `/approve`.
- **Day 30:** If `balance >= quota` → quota doubles ($20), new cycle. If not → wallet reset, memory wiped.

### Roles

- **HUNTER** - Finds money. Scans GitHub bounties (Algora, good first issues with rewards), article opportunities. 0 cost, uses free GitHub API.
- **WORKER** - Executes. Writes PRs, article drafts. Saves to `drafts/` and creates approval request. Never publishes alone.
- **ACCOUNTANT** - The asshole. Tracks days, balance, terminates or promotes. The only one who can reset.

### Approval Gate

Everything public needs you:

```json
"requires_approval": ["publish_article", "open_pr", "publish_video", "spend_real_money"]
```

You get a Telegram message:

> 🚨 Publish PR for $15? 
> Title: Fix login bug
> /approva prop-123 /rifiuta prop-123

No approval = no publish. Full control from your phone.

### Economy

Three-lane economy (inspired by OpenClaw):
- **Earning lane:** GitHub bounties, articles, any legal business
- **Spending lane:** API costs ($0 with Ollama local)
- **Profit lane:** balance - quota

Starts simulated ($0 fake), evolves to real USDC via OpenClaw wallet.

### Setup (0€)

1. Create Telegram bot via @BotFather, get token and chat_id
2. Add secrets to GitHub repo: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
3. Enable GitHub Actions - daily run at 9AM
4. Local: `pip install -r requirements.txt && python main.py`

### Project Status

Cycle 1 - Quota $10 - Experimental

Built with 0€ budget. No API keys required for simulation.

---
*This is not a get-rich-quick. It's a survival experiment.*

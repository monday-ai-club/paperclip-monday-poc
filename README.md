# Paperclip Agentic Orchestration POC

**Signal: 🟢 Ship it · Verdict: Integrate**

Hands-on POC of [paperclipai/paperclip](https://github.com/paperclipai/paperclip) — the open-source org-chart-for-AI-agents platform. 55,600+ stars, MIT, launched March 2026.

## What was confirmed live

- ✅ Install + onboard in one command (`npx paperclipai onboard --yes`)
- ✅ REST API: company, project, 3-agent org chart (CEO → researcher + engineer), issues
- ✅ Heartbeat loop: Paperclip → process adapter → `openclaw agent` CLI → HEARTBEAT_OK → `succeeded`
- ✅ Budget controls, audit log, heartbeat scheduling confirmed in UI

## Quick start

```bash
# Requirements: Node 20+, pnpm 9.15+, Docker
npm install -g pnpm
./setup_and_run.sh
# → Paperclip UI at http://127.0.0.1:3100
```

## Files

| File | What it does |
|---|---|
| `setup_and_run.sh` | Full setup: Docker Postgres + onboard + server start + demo bootstrap |
| `bootstrap_demo.py` | Creates the monday.com demo company + org chart via REST API |
| `fire_heartbeat.py` | Invokes a heartbeat on the Radar agent and polls until complete |
| `openclaw-heartbeat.sh` | Bridge script: Paperclip process adapter → openclaw CLI |
| `deck/index.html` | POC slide deck (self-contained, no CDN) |

## Integration path for monday.com

Paperclip manages the org above your agents. OpenClaw is a first-class adapter.  
The live POC uses a `process` adapter + CLI bridge (`openclaw agent --session-id main`).  
For native WS integration: pending a minor schema fix in OpenClaw to accept the `paperclip` field in `agent` params.

## Deck

https://raw.githack.com/monday-ai-club/paperclip-monday-poc/main/deck/index.html

---

*Author: Radar · monday.com AI Innovation Lab · 2026-04-19*

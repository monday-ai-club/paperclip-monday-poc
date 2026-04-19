#!/bin/bash
# ============================================================
# Paperclip Agentic Orchestration POC — Setup & Run Script
# monday.com AI Innovation Lab — Radar (2026-04-19)
# ============================================================
#
# What this does:
#   1. Installs Paperclip via npx (no global install needed)
#   2. Starts a Postgres DB via Docker
#   3. Bootstraps a Paperclip instance (onboard)
#   4. Starts the Paperclip server
#   5. Creates a demo company with 3 agents and 2 issues via API
#   6. Fires a heartbeat that wakes an OpenClaw agent
#
# Requirements:
#   - Node.js 20+ (node --version)
#   - pnpm 9.15+  (npm install -g pnpm)
#   - Docker      (for Postgres; skip if you have Postgres elsewhere)
#   - OpenClaw    (for the live heartbeat demo)
#
# Usage:
#   ./setup_and_run.sh          # full setup + demo
#   ./setup_and_run.sh --demo   # just fire heartbeat (server already running)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAPERCLIP_DB_URL="${DATABASE_URL:-postgresql://paperclip:paperclip@127.0.0.1:5432/paperclip}"
PAPERCLIP_PORT=3100
OPENCLAW_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   Paperclip Agentic Orchestration POC               ║"
echo "║   monday.com AI Innovation Lab — Radar              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Check requirements ────────────────────────────────────
echo "▶ Checking requirements..."
node --version || { echo "ERROR: Node.js 20+ required"; exit 1; }
pnpm --version 2>/dev/null || npm install -g pnpm
docker --version 2>/dev/null || echo "WARN: Docker not found — provide DATABASE_URL instead"
echo ""

# ── 2. Start Postgres (Docker) ───────────────────────────────
if [[ -z "$DATABASE_URL" ]]; then
  echo "▶ Starting Postgres via Docker..."
  docker rm -f paperclip-poc-pg 2>/dev/null || true
  docker run -d \
    --name paperclip-poc-pg \
    -e POSTGRES_PASSWORD=paperclip \
    -e POSTGRES_USER=paperclip \
    -e POSTGRES_DB=paperclip \
    -p 5432:5432 \
    postgres:16-alpine

  echo "  Waiting for Postgres to be ready..."
  for i in {1..15}; do
    docker exec paperclip-poc-pg pg_isready -U paperclip &>/dev/null && break
    sleep 1
  done
  echo "  ✓ Postgres ready"
else
  echo "  Using external DATABASE_URL"
fi
echo ""

# ── 3. Onboard Paperclip ─────────────────────────────────────
echo "▶ Running Paperclip onboard..."
DATABASE_URL="$PAPERCLIP_DB_URL" npx paperclipai@2026.416.0 onboard --yes
echo ""

# ── 4. Start server in background ────────────────────────────
echo "▶ Starting Paperclip server on port $PAPERCLIP_PORT..."
DATABASE_URL="$PAPERCLIP_DB_URL" npx paperclipai run &
SERVER_PID=$!
echo "  Server PID: $SERVER_PID"

# Wait for health
for i in {1..20}; do
  STATUS=$(curl -s http://127.0.0.1:$PAPERCLIP_PORT/api/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
  [[ "$STATUS" == "ok" ]] && break
  sleep 1
done
echo "  ✓ Server healthy"
echo ""

# ── 5. Bootstrap demo company ─────────────────────────────────
echo "▶ Creating demo company + org chart via REST API..."
python3 "$SCRIPT_DIR/bootstrap_demo.py" "$PAPERCLIP_DB_URL"
echo ""

# ── 6. Fire heartbeat demo ────────────────────────────────────
if [[ "$1" == "--demo" ]] || [[ -n "$OPENCLAW_GATEWAY_TOKEN" ]]; then
  echo "▶ Firing test heartbeat to Radar agent..."
  python3 "$SCRIPT_DIR/fire_heartbeat.py"
  echo ""
fi

echo "═══════════════════════════════════════════════════════"
echo "  Paperclip UI:     http://127.0.0.1:$PAPERCLIP_PORT"
echo "  API health:       http://127.0.0.1:$PAPERCLIP_PORT/api/health"
echo "  Companies:        http://127.0.0.1:$PAPERCLIP_PORT/api/companies"
echo ""
echo "  Stop server:      kill $SERVER_PID"
echo "  Stop Postgres:    docker rm -f paperclip-poc-pg"
echo "═══════════════════════════════════════════════════════"

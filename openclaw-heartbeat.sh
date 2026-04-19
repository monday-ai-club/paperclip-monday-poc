#!/bin/bash
# ============================================================
# openclaw-heartbeat.sh
# Paperclip -> OpenClaw heartbeat bridge script
#
# Paperclip's process adapter runs this script when it fires
# a heartbeat on the Radar agent. The script calls the local
# OpenClaw CLI to wake the main agent session.
#
# Env vars injected by Paperclip:
#   PAPERCLIP_AGENT_ID    — the Paperclip agent UUID
#   PAPERCLIP_COMPANY_ID  — the company UUID
#   PAPERCLIP_API_URL     — Paperclip REST API base URL
# ============================================================

PAPERCLIP_AGENT_ID="${PAPERCLIP_AGENT_ID:-unknown}"
PAPERCLIP_API_URL="${PAPERCLIP_API_URL:-http://127.0.0.1:3100}"

MSG="[Paperclip Heartbeat] agentId=${PAPERCLIP_AGENT_ID} apiUrl=${PAPERCLIP_API_URL}. Paperclip has woken you via scheduled heartbeat. Check http://127.0.0.1:3100/api/companies for open issues assigned to the Radar agent. Respond with HEARTBEAT_OK if nothing needs attention."

# Wake the main OpenClaw session
openclaw agent \
  --session-id main \
  --message "$MSG" 2>&1

EXIT_CODE=$?
echo "exit=${EXIT_CODE} heartbeat-sent agentId=${PAPERCLIP_AGENT_ID}"
exit $EXIT_CODE

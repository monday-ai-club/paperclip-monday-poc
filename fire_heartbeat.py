#!/usr/bin/env python3
"""
fire_heartbeat.py — Invokes a Paperclip heartbeat on the Radar agent and polls until complete.

Usage: python3 fire_heartbeat.py [agent_id]

Shows: run ID, status, stdout log excerpt
"""
import json
import sys
import time
import urllib.request

BASE_URL = "http://127.0.0.1:3100"

def api(method, path, body=None):
    url = f"{BASE_URL}/api{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def main():
    # Find Radar agent
    companies = api("GET", "/companies")
    if not companies:
        print("ERROR: No companies found. Run bootstrap_demo.py first.")
        sys.exit(1)

    company_id = companies[0]["id"]
    agents = api("GET", f"/companies/{company_id}/agents")
    radar = next((a for a in agents if a["role"] == "researcher"), None)
    if not radar:
        print("ERROR: Radar agent not found. Run bootstrap_demo.py first.")
        sys.exit(1)

    agent_id = sys.argv[1] if len(sys.argv) > 1 else radar["id"]
    print(f"  Firing heartbeat on agent: {radar['name']} ({agent_id})")

    # Invoke heartbeat
    run = api("POST", f"/agents/{agent_id}/heartbeat/invoke", {
        "source": "on_demand",
        "trigger": "manual"
    })
    run_id = run["id"]
    print(f"  Run ID: {run_id}")
    print(f"  Status: {run['status']}")

    # Poll until complete
    print("  Polling", end="", flush=True)
    for _ in range(30):
        time.sleep(2)
        result = api("GET", f"/heartbeat-runs/{run_id}")
        status = result.get("status")
        print(".", end="", flush=True)
        if status in ("succeeded", "failed", "cancelled"):
            break
    print()

    print(f"  Final status: {result.get('status')}")
    if result.get("error"):
        print(f"  Error: {result['error']}")

    # Fetch log
    try:
        log_data = api("GET", f"/heartbeat-runs/{run_id}/log")
        content = log_data.get("content", "")
        lines = []
        for line in content.split("\n"):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                chunk = entry.get("chunk", "")
                # Skip noise
                if any(x in chunk for x in ["plugins.allow", "plugins.entries", "Config warnings"]):
                    continue
                lines.append(f"  {entry.get('stream','?')}: {chunk.rstrip()}")
            except Exception:
                pass
        if lines:
            print("\n  ── Heartbeat log ──")
            for l in lines:
                print(l[:120])
    except Exception as e:
        print(f"  (log fetch failed: {e})")

    print()
    succeeded = result.get("status") == "succeeded"
    print("  ✅ Heartbeat loop PASSED" if succeeded else "  ❌ Heartbeat failed")
    sys.exit(0 if succeeded else 1)

if __name__ == "__main__":
    main()

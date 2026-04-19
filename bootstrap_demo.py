#!/usr/bin/env python3
"""
bootstrap_demo.py — Creates the monday.com demo company in a fresh Paperclip instance.

Usage: python3 bootstrap_demo.py [database_url]

Creates:
  - Company: "Monday AI Innovation POC"
  - Project: "Agentic Orchestration Research"
  - Agents: ResearchCEO (ceo), Radar (researcher), CodeAgent (engineer)
  - Issues: MON-1 (evaluate Paperclip), MON-2 (wire OpenClaw heartbeat)
"""
import json
import sys
import urllib.request
import urllib.error

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
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} on {method} {path}: {e.read().decode()[:200]}")
        return None

def main():
    # Health check
    health = api("GET", "/health")
    if not health or health.get("status") != "ok":
        print("ERROR: Paperclip server not healthy at", BASE_URL)
        sys.exit(1)
    print(f"  ✓ Server version {health.get('version')} healthy")

    # Check existing companies
    companies = api("GET", "/companies") or []
    if companies:
        print(f"  Found {len(companies)} existing company/companies")
        company = companies[0]
        company_id = company["id"]
        print(f"  Using existing: {company['name']} ({company_id})")
    else:
        # Create company
        company = api("POST", "/companies", {
            "name": "Monday AI Innovation POC",
            "mission": "Evaluate and ship agentic orchestration patterns for monday.com — 3 production-ready agent workflows by Q2 2026."
        })
        if not company:
            print("ERROR: Failed to create company")
            sys.exit(1)
        company_id = company["id"]
        print(f"  ✓ Company: {company['name']} ({company_id})")

    # Check existing project
    projects = api("GET", f"/companies/{company_id}/projects") or []
    if projects:
        project_id = projects[0]["id"]
        print(f"  Using existing project: {projects[0]['name']}")
    else:
        project = api("POST", f"/companies/{company_id}/projects", {
            "name": "Agentic Orchestration Research",
            "goal": "Research, evaluate and POC agentic orchestration frameworks. Produce demo decks and integration recommendations for monday.com."
        })
        project_id = project["id"]
        print(f"  ✓ Project: {project['name']} ({project_id})")

    # Check existing agents
    agents = api("GET", f"/companies/{company_id}/agents") or []
    agent_map = {a["role"]: a["id"] for a in agents}

    if "ceo" not in agent_map:
        ceo = api("POST", f"/companies/{company_id}/agents", {
            "name": "ResearchCEO",
            "role": "ceo",
            "description": "Owns overall research strategy. Decomposes the mission into projects, delegates to specialized agents, reviews findings.",
            "runtime": "claude",
            "budgetMonthlyCents": 1000
        })
        agent_map["ceo"] = ceo["id"]
        print(f"  ✓ Agent: ResearchCEO ({ceo['id']})")
    else:
        print(f"  Using existing CEO: {agent_map['ceo']}")

    if "researcher" not in agent_map:
        researcher = api("POST", f"/companies/{company_id}/agents", {
            "name": "Radar",
            "role": "researcher",
            "description": "Senior tech intelligence agent. Scans GitHub trending, arXiv, Hugging Face. Runs POCs. Produces structured radar reports.",
            "adapterType": "process",
            "adapterConfig": {
                "command": "./openclaw-heartbeat.sh",
                "timeoutMs": 60000
            },
            "budgetMonthlyCents": 500
        })
        agent_map["researcher"] = researcher["id"]
        print(f"  ✓ Agent: Radar ({researcher['id']})")
    else:
        print(f"  Using existing Radar: {agent_map['researcher']}")

    if "engineer" not in agent_map:
        engineer = api("POST", f"/companies/{company_id}/agents", {
            "name": "CodeAgent",
            "role": "engineer",
            "description": "Implements POC code, runs experiments. Reports to ResearchCEO.",
            "runtime": "claude",
            "reportsTo": agent_map["ceo"],
            "budgetMonthlyCents": 500
        })
        agent_map["engineer"] = engineer["id"]
        print(f"  ✓ Agent: CodeAgent ({engineer['id']})")
    else:
        print(f"  Using existing engineer: {agent_map['engineer']}")

    # Create issues if none exist
    issues = api("GET", f"/companies/{company_id}/issues") or []
    if not issues:
        # Create via CLI-style direct API
        import subprocess
        result = subprocess.run([
            "npx", "paperclipai", "issue", "create",
            "--api-base", BASE_URL,
            "--company-id", company_id,
            "--project-id", project_id,
            "--title", "Evaluate Paperclip agentic orchestration framework",
            "--description", "POC of paperclipai/paperclip (55k★ MIT). Install, create org chart, test heartbeat scheduling + budget controls + audit log. Produce Radar report.",
            "--assignee-agent-id", agent_map["researcher"],
            "--priority", "high",
            "--status", "in_progress",
            "--json"
        ], capture_output=True, text=True)
        if result.returncode == 0:
            issue1 = json.loads(result.stdout)
            print(f"  ✓ Issue: {issue1.get('identifier')} - {issue1.get('title')}")

        result2 = subprocess.run([
            "npx", "paperclipai", "issue", "create",
            "--api-base", BASE_URL,
            "--company-id", company_id,
            "--project-id", project_id,
            "--title", "Wire OpenClaw as Paperclip heartbeat worker",
            "--description", "Configure OpenClaw (this instance) as an agent inside Paperclip via heartbeat API. Document the integration path.",
            "--assignee-agent-id", agent_map["engineer"],
            "--priority", "high",
            "--status", "todo",
            "--json"
        ], capture_output=True, text=True)
        if result2.returncode == 0:
            issue2 = json.loads(result2.stdout)
            print(f"  ✓ Issue: {issue2.get('identifier')} - {issue2.get('title')}")
    else:
        print(f"  {len(issues)} existing issues found")

    print()
    print(f"  Company ID:   {company_id}")
    print(f"  Project ID:   {project_id}")
    print(f"  CEO:          {agent_map.get('ceo')}")
    print(f"  Researcher:   {agent_map.get('researcher')}")
    print(f"  Engineer:     {agent_map.get('engineer')}")
    print()
    print("  Bootstrap complete ✓")

if __name__ == "__main__":
    main()

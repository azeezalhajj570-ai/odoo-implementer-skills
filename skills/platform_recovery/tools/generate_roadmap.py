#!/usr/bin/env python3
"""
Generate a phased rebuild roadmap from recovery constraints.

Usage:
    python generate_roadmap.py --team-size 12 --start-date 2026-08-01
"""

import argparse
import json
from datetime import datetime, timedelta


PHASES = [
    {"name": "Foundation", "months": 3, "focus": "PostgreSQL, Redis, FastAPI, auth, multi-tenancy, audit, read-only connectors"},
    {"name": "Real Digital Twin", "months": 3, "focus": "Graph DB backend, event-driven sync, delta history, staleness detection"},
    {"name": "AI Layer", "months": 3, "focus": "LLM integration, RAG, embeddings, vector memory, human-in-the-loop"},
    {"name": "Execution", "months": 3, "focus": "Sandboxed workflows, staging promotion, rollback, migration dry-run"},
    {"name": "Operations", "months": 6, "focus": "Monitoring, incident response, optimization from data, enterprise dashboard"},
    {"name": "Scale", "months": 6, "focus": "Horizontal scaling, fleet management, enterprise governance"},
]


def generate_roadmap(team_size: int, start_date: str) -> list:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    roadmap = []
    for phase in PHASES:
        end = start + timedelta(days=phase["months"] * 30)
        roadmap.append({
            "phase": phase["name"],
            "duration_months": phase["months"],
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "focus": phase["focus"],
            "team_size": team_size,
        })
        start = end
    return roadmap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--team-size", type=int, default=12)
    parser.add_argument("--start-date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()

    roadmap = generate_roadmap(args.team_size, args.start_date)
    print(json.dumps(roadmap, indent=2))


if __name__ == "__main__":
    main()

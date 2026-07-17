#!/usr/bin/env python3
"""
Generate a due diligence scorecard from structured findings.

Usage:
    python generate_scorecard.py --findings findings.json
"""

import json
import sys
from pathlib import Path


SCORECARD_TEMPLATE = {
    "Architecture": 0,
    "AI Design": 0,
    "Odoo Expertise": 0,
    "Software Engineering": 0,
    "Scalability": 0,
    "Security": 0,
    "Maintainability": 0,
    "Extensibility": 0,
    "Production Readiness": 0,
    "Innovation": 0,
    "Commercial Potential": 0,
}


def generate_scorecard(findings: list) -> dict:
    scores = dict(SCORECARD_TEMPLATE)
    for finding in findings:
        dim = finding.get("dimension")
        score = finding.get("score")
        if dim in scores and isinstance(score, (int, float)):
            scores[dim] = max(0, min(10, score))
    return scores


def main(findings_path: str):
    path = Path(findings_path)
    if not path.exists():
        print(f"File not found: {findings_path}")
        sys.exit(1)

    findings = json.loads(path.read_text())
    scorecard = generate_scorecard(findings)
    print(json.dumps(scorecard, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "findings.json")

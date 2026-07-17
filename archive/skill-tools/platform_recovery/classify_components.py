#!/usr/bin/env python3
"""
Classify project components as KEEP, MERGE, or DELETE based on due diligence findings.

Usage:
    python classify_components.py --findings findings.json
"""

import json
import sys
from pathlib import Path


def classify(findings: list) -> dict:
    keep = []
    merge = []
    delete = []

    for finding in findings:
        name = finding.get("component", "")
        verdict = finding.get("verdict", "").lower()
        if verdict == "keep":
            keep.append(name)
        elif verdict == "merge":
            merge.append({
                "component": name,
                "reason": finding.get("reason", ""),
                "target": finding.get("merge_into", ""),
            })
        elif verdict == "delete":
            delete.append({
                "component": name,
                "reason": finding.get("reason", ""),
            })

    return {"keep": keep, "merge": merge, "delete": delete}


def main(findings_path: str):
    path = Path(findings_path)
    if not path.exists():
        print(f"File not found: {findings_path}")
        sys.exit(1)

    findings = json.loads(path.read_text())
    result = classify(findings)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "findings.json")

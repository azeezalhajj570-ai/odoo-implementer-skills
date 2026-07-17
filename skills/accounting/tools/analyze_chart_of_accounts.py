"""
Accounting Chart of Accounts Analyzer Tool

Analyzes a chart of accounts configuration and returns insights about
account types, group hierarchy, missing defaults, and recommendations.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_chart_of_accounts(accounts: Optional[List[dict]] = None,
                                groups: Optional[List[dict]] = None,
                                db_connection: Optional[str] = None) -> dict:
    """
    Analyze a chart of accounts configuration.

    Args:
        accounts: List of account dicts with code, name, account_type, reconcile
        groups: List of account group dicts with code_prefix_start, code_prefix_end
        db_connection: Optional database connection string

    Returns:
        Analysis results with counts, issues, and recommendations
    """
    results = {
        "account_count": 0,
        "group_count": 0,
        "account_types": {},
        "reconcilable_count": 0,
        "issues": [],
        "recommendations": [],
    }

    if accounts:
        results["account_count"] = len(accounts)
        for acc in accounts:
            acc_type = acc.get("account_type", "unknown")
            results["account_types"][acc_type] = results["account_types"].get(acc_type, 0) + 1
            if acc.get("reconcile"):
                results["reconcilable_count"] += 1

            code = acc.get("code", "")
            if code and not code.isdigit():
                results["issues"].append(
                    f"Account '{acc.get('name')}' has non-numeric code '{code}'"
                )

        if not any(t.startswith("asset") or t.startswith("liability") for t in results["account_types"]):
            results["issues"].append("No balance sheet account types found")

        if results["account_count"] < 20:
            results["recommendations"].append(
                "Chart of accounts is small. Verify localization package is installed."
            )

    if groups:
        results["group_count"] = len(groups)
        for grp in groups:
            start = grp.get("code_prefix_start", "")
            end = grp.get("code_prefix_end", "")
            if start and end and start > end:
                results["issues"].append(
                    f"Group '{grp.get('name')}' has prefix start greater than end"
                )

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_chart_of_accounts",
        description="Analyze chart of accounts for types, groups, and configuration issues",
        parameters={
            "type": "object",
            "properties": {
                "accounts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of account records"
                },
                "groups": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of account group records"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Analysis with counts, issues, and recommendations"
        },
        skill_id="skill_accounting",
        category="analyzer",
        fn=analyze_chart_of_accounts,
    ))


tools = [
    {
        "name": "analyze_chart_of_accounts",
        "description": "Analyze chart of accounts for types, groups, and configuration issues",
        "parameters": {
            "type": "object",
            "properties": {
                "accounts": {"type": "array", "items": {"type": "object"}},
                "groups": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_chart_of_accounts,
    }
]

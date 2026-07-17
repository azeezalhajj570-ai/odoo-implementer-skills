"""
Accounting Reconciliation Validator Tool

Validates bank reconciliation configuration and statement data.
Checks for unmatched statement lines, missing reconciliation models,
and outstanding account setup.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def validate_reconciliation(statement_lines: Optional[List[dict]] = None,
                              models: Optional[List[dict]] = None,
                              journals: Optional[List[dict]] = None,
                              config: Optional[dict] = None) -> dict:
    """
    Validate bank reconciliation configuration.

    Args:
        statement_lines: List of bank statement line dicts
        models: List of reconciliation model dicts
        journals: List of bank/cash journal dicts
        config: Optional reconciliation configuration

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if journals:
        for journal in journals:
            if journal.get("type") in ("bank", "cash"):
                if not journal.get("default_account_id"):
                    results["issues"].append(
                        f"Journal '{journal.get('name')}' has no default account"
                    )
                    results["valid"] = False

    if statement_lines:
        unmatched = [line for line in statement_lines if not line.get("is_reconciled")]
        if unmatched:
            results["warnings"].append(
                f"{len(unmatched)} statement lines are not reconciled"
            )

    if models:
        model_types = {m.get("rule_type") for m in models}
        if "invoice_matching" not in model_types:
            results["recommendations"].append(
                "Add an invoice matching reconciliation model to auto-match payments"
            )
        if "writeoff_button" not in model_types:
            results["recommendations"].append(
                "Add a write-off button model for small differences"
            )
    else:
        results["recommendations"].append(
            "No reconciliation models configured. Consider creating invoice matching rules."
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_reconciliation",
        description="Validate bank reconciliation configuration and statement line status",
        parameters={
            "type": "object",
            "properties": {
                "statement_lines": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Bank statement lines"
                },
                "models": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Reconciliation models"
                },
                "journals": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Bank/cash journals"
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_accounting",
        category="validator",
        fn=validate_reconciliation,
    ))


tools = [
    {
        "name": "validate_reconciliation",
        "description": "Validate bank reconciliation configuration and statement line status",
        "parameters": {
            "type": "object",
            "properties": {
                "statement_lines": {"type": "array", "items": {"type": "object"}},
                "models": {"type": "array", "items": {"type": "object"}},
                "journals": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "validator",
        "fn": validate_reconciliation,
    }
]

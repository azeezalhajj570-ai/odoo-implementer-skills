"""
CRM Lead Scoring Validator Tool

Validates a Predictive Lead Scoring configuration.
Checks frequency table fields, config parameters, data sufficiency.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def validate_lead_scoring(pls_fields: Optional[List[str]] = None,
                          won_count: int = 0,
                          lost_count: int = 0,
                          config: Optional[dict] = None) -> dict:
    """
    Validate Predictive Lead Scoring configuration.

    Args:
        pls_fields: List of field names configured for PLS
        won_count: Number of won leads in training data
        lost_count: Number of lost leads in training data
        config: Optional PLS configuration dict

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    # Check field configuration
    default_fields = {
        "phone_state", "email_state", "state_id", "country_id",
        "source_id", "lang_id", "tag_ids"
    }

    if pls_fields:
        missing_defaults = default_fields - set(pls_fields)
        if missing_defaults:
            results["warnings"].append(
                f"Missing default PLS fields: {missing_defaults}"
            )

    # Check data sufficiency
    total = won_count + lost_count
    if total == 0:
        results["issues"].append(
            "No won/lost data available. PLS requires historical "
            "conversion data to produce meaningful scores."
        )
        results["valid"] = False
    elif total < 50:
        results["warnings"].append(
            f"Only {total} closed leads. PLS becomes more reliable "
            f"with 100+ closed leads per team."
        )
    elif total < 20:
        results["issues"].append(
            f"Only {total} closed leads. Insufficient for reliable "
            f"Naive Bayes probability estimates."
        )

    # Check config
    if config:
        start_date = config.get("pls_start_date")
        if start_date:
            results["recommendations"].append(
                f"PLS training window starts: {start_date}"
            )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_lead_scoring",
        description="Validate Predictive Lead Scoring configuration",
        parameters={
            "type": "object",
            "properties": {
                "pls_fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "PLS field names"
                },
                "won_count": {
                    "type": "integer",
                    "description": "Won lead count"
                },
                "lost_count": {
                    "type": "integer",
                    "description": "Lost lead count"
                },
                "config": {
                    "type": "object",
                    "description": "PLS configuration"
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_crm",
        category="validator",
        fn=validate_lead_scoring,
    ))


tools = [
    {
        "name": "validate_lead_scoring",
        "description": "Validate Predictive Lead Scoring configuration",
        "parameters": {
            "type": "object",
            "properties": {
                "pls_fields": {"type": "array", "items": {"type": "string"}},
                "won_count": {"type": "integer"},
                "lost_count": {"type": "integer"},
                "config": {"type": "object"}
            }
        },
        "category": "validator",
        "fn": validate_lead_scoring,
    }
]

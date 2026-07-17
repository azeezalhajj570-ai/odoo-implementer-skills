"""
Marketing Configuration Validator Tool

Validates the overall marketing configuration including:
mass_mailing settings, Marketing Automation configuration,
IAP services, Social Marketing accounts.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def validate_marketing_config(config: Optional[dict] = None,
                              check_iap: bool = True,
                              check_social: bool = True) -> dict:
    """
    Validate full marketing configuration.

    Args:
        config: Marketing configuration dict
        check_iap: Whether to check IAP credit availability
        check_social: Whether to check social media accounts

    Returns:
        Validation results
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if config:
        # Check mass_mailing settings
        mm = config.get("mass_mailing", {})
        if not mm.get("outgoing_mail_server"):
            results["warnings"].append(
                "No dedicated outgoing mail server configured for mass mailings"
            )

        # Check marketing automation
        ma = config.get("marketing_automation", {})
        if ma.get("campaign_count", 0) == 0:
            results["recommendations"].append(
                "Start with a Welcome Flow campaign template"
            )

        # Check UTM
        utm = config.get("utm", {})
        if not utm.get("campaigns"):
            results["recommendations"].append(
                "Create UTM campaigns for tracking marketing attribution"
            )

    if check_iap:
        results["recommendations"].append(
            "Verify IAP credit balance for SMS and Lead Enrichment services"
        )

    if check_social:
        results["recommendations"].append(
            "Connect social media accounts in Social Marketing settings"
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_marketing_config",
        description="Validate full marketing configuration",
        parameters={
            "type": "object",
            "properties": {
                "config": {"type": "object"},
                "check_iap": {"type": "boolean"},
                "check_social": {"type": "boolean"}
            }
        },
        returns={"type": "object"},
        skill_id="skill_marketing",
        category="validator",
        fn=validate_marketing_config,
    ))


tools = [
    {
        "name": "validate_marketing_config",
        "description": "Validate full marketing configuration",
        "parameters": {
            "type": "object",
            "properties": {
                "config": {"type": "object"},
                "check_iap": {"type": "boolean"},
                "check_social": {"type": "boolean"}
            }
        },
        "category": "validator",
        "fn": validate_marketing_config,
    }
]

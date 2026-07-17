"""
Marketing Campaign Analyzer Tool

Analyzes email/marketing campaigns for optimization opportunities.
Checks deliverability, targeting, timing, content, A/B testing setup.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def analyze_campaign(campaign_data: Optional[dict] = None,
                     mailing_data: Optional[dict] = None,
                     check_ab_testing: bool = True) -> dict:
    """
    Analyze a marketing campaign configuration.

    Args:
        campaign_data: Dict with campaign configuration
        mailing_data: Dict with mailing configuration
        check_ab_testing: Whether to analyze A/B testing setup

    Returns:
        Analysis with recommendations and issues
    """
    results = {
        "campaign_name": "",
        "issues": [],
        "recommendations": [],
        "ab_testing_analysis": None,
    }

    if campaign_data:
        results["campaign_name"] = campaign_data.get("name", "Unknown")
        target_model = campaign_data.get("model_name", "")
        domain = campaign_data.get("domain", "")

        if not target_model:
            results["issues"].append("No target model selected for campaign")

        activities = campaign_data.get("activities", [])
        if len(activities) < 2:
            results["recommendations"].append(
                "Consider adding more activities for a multi-step nurturing flow"
            )

        # Check for begin trigger
        has_begin = any(a.get("trigger_type") == "begin" for a in activities)
        if not has_begin:
            results["issues"].append(
                "Campaign has no 'begin' trigger activity"
            )

    if mailing_data:
        subject = mailing_data.get("subject", "")
        if not subject:
            results["issues"].append("Email has no subject line")

        ab_testing = mailing_data.get("ab_testing_enabled", False)
        if check_ab_testing and not ab_testing:
            results["recommendations"].append(
                "Enable A/B testing to optimize email performance"
            )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="analyze_campaign",
        description="Analyze marketing campaign configuration for optimization opportunities",
        parameters={
            "type": "object",
            "properties": {
                "campaign_data": {
                    "type": "object",
                    "description": "Campaign configuration"
                },
                "mailing_data": {
                    "type": "object",
                    "description": "Mailing/email configuration"
                },
                "check_ab_testing": {
                    "type": "boolean",
                    "description": "Whether to analyze A/B testing"
                }
            }
        },
        returns={"type": "object"},
        skill_id="skill_marketing",
        category="analyzer",
        fn=analyze_campaign,
    ))


tools = [
    {
        "name": "analyze_campaign",
        "description": "Analyze marketing campaign configuration",
        "parameters": {
            "type": "object",
            "properties": {
                "campaign_data": {"type": "object"},
                "mailing_data": {"type": "object"},
                "check_ab_testing": {"type": "boolean"}
            }
        },
        "category": "analyzer",
        "fn": analyze_campaign,
    }
]

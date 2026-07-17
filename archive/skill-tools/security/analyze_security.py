"""
Security Configuration Analyzer Tool

Analyzes a security configuration (groups, ACLs, record rules) for
common issues such as missing ACLs, overly broad rules, or conflicts.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_security(groups: Optional[List[dict]] = None,
                     acls: Optional[List[dict]] = None,
                     rules: Optional[List[dict]] = None,
                     models: Optional[List[str]] = None) -> dict:
    """
    Analyze Odoo security configuration.

    Args:
        groups: List of group definitions
        acls: List of ACL definitions
        rules: List of record rule definitions
        models: List of model names to check

    Returns:
        Analysis results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    acl_models = set()
    if acls:
        for acl in acls:
            model = acl.get("model")
            if model:
                acl_models.add(model)
            if acl.get("perm_unlink") and not acl.get("group_id"):
                results["warnings"].append(
                    f"ACL for {model} grants unlink to all users."
                )

    if models:
        missing_acls = set(models) - acl_models
        if missing_acls:
            results["issues"].append(
                f"Models missing ACLs: {sorted(missing_acls)}"
            )
            results["valid"] = False

    if rules:
        for rule in rules:
            domain = rule.get("domain_force", "")
            if domain == "[(1,'=',1)]" and rule.get("global"):
                results["warnings"].append(
                    f"Global rule {rule.get('name')} allows all records."
                )

    if groups:
        results["recommendations"].append(
            f"Review {len(groups)} groups for least-privilege alignment."
        )

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_security",
        description="Analyze Odoo security configuration for issues",
        parameters={
            "type": "object",
            "properties": {
                "groups": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Group definitions"
                },
                "acls": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "ACL definitions"
                },
                "rules": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Record rule definitions"
                },
                "models": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Model names to check"
                }
            }
        },
        returns={"type": "object", "description": "Security analysis results"},
        skill_id="skill_security",
        category="analyzer",
        fn=analyze_security,
    ))


tools = [
    {
        "name": "analyze_security",
        "description": "Analyze Odoo security configuration for issues",
        "parameters": {
            "type": "object",
            "properties": {
                "groups": {"type": "array", "items": {"type": "object"}},
                "acls": {"type": "array", "items": {"type": "object"}},
                "rules": {"type": "array", "items": {"type": "object"}},
                "models": {"type": "array", "items": {"type": "string"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_security,
    }
]

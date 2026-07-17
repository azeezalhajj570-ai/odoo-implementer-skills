"""
ACL Validator Tool

Validates access control lists against a set of models and required permissions.
"""

from typing import Any, Dict, List, Optional


def validate_acl(acls: Optional[List[dict]] = None,
                 required_models: Optional[List[str]] = None,
                 min_permissions: Optional[List[str]] = None) -> dict:
    """
    Validate ACLs for required models and permissions.

    Args:
        acls: List of ACL definitions
        required_models: Models that must have ACLs
        min_permissions: Minimum permissions each ACL should have (read, write, create, unlink)

    Returns:
        Validation results with missing or weak ACLs
    """
    results = {
        "valid": True,
        "missing_models": [],
        "weak_acls": [],
        "recommendations": [],
    }

    min_permissions = min_permissions or ["read"]
    acl_map = {}
    if acls:
        for acl in acls:
            model = acl.get("model")
            if model:
                acl_map.setdefault(model, []).append(acl)

    if required_models:
        for model in required_models:
            if model not in acl_map:
                results["missing_models"].append(model)
                results["valid"] = False
                continue

            for acl in acl_map[model]:
                missing = [p for p in min_permissions if not acl.get(f"perm_{p}")]
                if missing:
                    results["weak_acls"].append({
                        "model": model,
                        "acl": acl.get("name"),
                        "missing_permissions": missing,
                    })
                    results["valid"] = False

    if not results["valid"]:
        results["recommendations"].append(
            "Add missing ACLs and ensure each model has at least read permission."
        )
    else:
        results["recommendations"].append(
            "All required models have ACLs with minimum permissions."
        )

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="validate_acl",
        description="Validate ACLs for required models and permissions",
        parameters={
            "type": "object",
            "properties": {
                "acls": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "ACL definitions"
                },
                "required_models": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required model names"
                },
                "min_permissions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Minimum permissions: read, write, create, unlink"
                }
            }
        },
        returns={"type": "object", "description": "ACL validation results"},
        skill_id="skill_security",
        category="validator",
        fn=validate_acl,
    ))


tools = [
    {
        "name": "validate_acl",
        "description": "Validate ACLs for required models and permissions",
        "parameters": {
            "type": "object",
            "properties": {
                "acls": {"type": "array", "items": {"type": "object"}},
                "required_models": {"type": "array", "items": {"type": "string"}},
                "min_permissions": {"type": "array", "items": {"type": "string"}}
            }
        },
        "category": "validator",
        "fn": validate_acl,
    }
]

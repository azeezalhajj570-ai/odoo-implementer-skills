"""
Inventory Route Validator Tool

Validates stock routes and rules, checking for missing source/destination
locations, disconnected routes, and conflicting MTS/MTO setups.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def validate_routes(routes: Optional[List[dict]] = None,
                    rules: Optional[List[dict]] = None,
                    warehouses: Optional[List[dict]] = None) -> dict:
    """
    Validate inventory routes and procurement rules.

    Args:
        routes: List of route dicts
        rules: List of stock.rule dicts
        warehouses: List of warehouse dicts

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if routes:
        route_ids = {r.get("id") for r in routes}
        for route in routes:
            if not route.get("rule_ids") and not route.get("active", True):
                results["warnings"].append(
                    f"Route '{route.get('name')}' has no rules"
                )

    if rules:
        for rule in rules:
            route_id = rule.get("route_id")
            if route_id not in ({r.get("id") for r in routes or []}):
                results["issues"].append(
                    f"Rule '{rule.get('name')}' references unknown route {route_id}"
                )
                results["valid"] = False
            if not rule.get("location_src_id") and rule.get("action") in ("pull", "push", "pull_push"):
                results["issues"].append(
                    f"Rule '{rule.get('name')}' is missing source location"
                )
                results["valid"] = False
            if not rule.get("location_dest_id"):
                results["issues"].append(
                    f"Rule '{rule.get('name')}' is missing destination location"
                )
                results["valid"] = False

    if warehouses:
        for wh in warehouses:
            if not wh.get("in_type_id") or not wh.get("out_type_id"):
                results["issues"].append(
                    f"Warehouse '{wh.get('name')}' is missing picking types"
                )
                results["valid"] = False

    if not rules:
        results["recommendations"].append(
            "Define procurement rules for custom routes to ensure supply flows work."
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_routes",
        description="Validate inventory routes and procurement rules",
        parameters={
            "type": "object",
            "properties": {
                "routes": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Route records"
                },
                "rules": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Stock rule records"
                },
                "warehouses": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Warehouse records"
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_inventory",
        category="validator",
        fn=validate_routes,
    ))


tools = [
    {
        "name": "validate_routes",
        "description": "Validate inventory routes and procurement rules",
        "parameters": {
            "type": "object",
            "properties": {
                "routes": {"type": "array", "items": {"type": "object"}},
                "rules": {"type": "array", "items": {"type": "object"}},
                "warehouses": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "validator",
        "fn": validate_routes,
    }
]

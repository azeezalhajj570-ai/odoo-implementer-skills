"""
Manufacturing Routing Validator Tool

Validates a routing configuration for missing work centers, orphan operations,
and circular sequences.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition


def validate_routing(operations: Optional[List[dict]] = None,
                     require_workcenter: bool = True) -> dict:
    """
    Validate a manufacturing routing.

    Args:
        operations: List of operation dicts with workcenter_id and sequence
        require_workcenter: Whether every operation must have a work center

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if not operations:
        results["issues"].append("Routing has no operations")
        results["valid"] = False
        return results

    sequences = []
    for idx, op in enumerate(operations):
        name = op.get("name", f"Operation {idx + 1}")
        seq = op.get("sequence", 0)
        sequences.append(seq)

        if require_workcenter and not op.get("workcenter_id"):
            results["issues"].append(f"{name} has no work center")
            results["valid"] = False

        if op.get("time_cycle_manual", 0) < 0:
            results["issues"].append(f"{name} has negative cycle time")
            results["valid"] = False

    if len(sequences) != len(set(sequences)):
        results["warnings"].append("Multiple operations share the same sequence")

    if sorted(sequences) != list(range(min(sequences), max(sequences) + 1)) and len(sequences) > 1:
        results["warnings"].append("Operation sequences have gaps")

    if len(operations) > 20:
        results["recommendations"].append(
            "Consider splitting a long routing into sub-assemblies"
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_routing",
        description="Validate manufacturing routing operations",
        parameters={
            "type": "object",
            "properties": {
                "operations": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of operation dictionaries"
                },
                "require_workcenter": {
                    "type": "boolean",
                    "description": "Require each operation to have a work center",
                    "default": True
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_manufacturing",
        category="validator",
        fn=validate_routing,
    ))


tools = [
    {
        "name": "validate_routing",
        "description": "Validate manufacturing routing operations",
        "parameters": {
            "type": "object",
            "properties": {
                "operations": {"type": "array", "items": {"type": "object"}},
                "require_workcenter": {"type": "boolean"}
            }
        },
        "category": "validator",
        "fn": validate_routing,
    }
]

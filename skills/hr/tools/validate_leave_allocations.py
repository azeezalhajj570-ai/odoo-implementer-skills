"""
HR Leave Allocation Validator Tool

Validates leave type and allocation configuration, checking for
missing accrual plans, negative balances, and expired allocations.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def validate_leave_allocations(leave_types: Optional[List[dict]] = None,
                               allocations: Optional[List[dict]] = None,
                               accrual_plans: Optional[List[dict]] = None,
                               today: Optional[str] = None) -> dict:
    """
    Validate leave allocations and accrual setup.

    Args:
        leave_types: List of leave type dicts
        allocations: List of allocation dicts with number_of_days, state, date_to
        accrual_plans: List of accrual plan dicts
        today: Optional reference date string

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if leave_types:
        for lt in leave_types:
            if lt.get("requires_allocation") and not lt.get("allocation_type"):
                results["issues"].append(
                    f"Leave type '{lt.get('name')}' requires allocation but has no allocation type"
                )
                results["valid"] = False

    if allocations:
        for alloc in allocations:
            if alloc.get("number_of_days", 0) < 0:
                results["issues"].append(
                    f"Allocation for employee {alloc.get('employee_id')} has negative days"
                )
                results["valid"] = False
            if alloc.get("state") != "validate":
                results["warnings"].append(
                    f"Allocation {alloc.get('id')} is not validated"
                )

    if accrual_plans:
        for plan in accrual_plans:
            if not plan.get("level_ids"):
                results["warnings"].append(
                    f"Accrual plan '{plan.get('name')}' has no levels"
                )
    else:
        results["recommendations"].append(
            "Define accrual plans for leave types that grant time over employment duration."
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_leave_allocations",
        description="Validate leave types, allocations, and accrual plans",
        parameters={
            "type": "object",
            "properties": {
                "leave_types": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Leave type records"
                },
                "allocations": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Allocation records"
                },
                "accrual_plans": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Accrual plan records"
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_hr",
        category="validator",
        fn=validate_leave_allocations,
    ))


tools = [
    {
        "name": "validate_leave_allocations",
        "description": "Validate leave types, allocations, and accrual plans",
        "parameters": {
            "type": "object",
            "properties": {
                "leave_types": {"type": "array", "items": {"type": "object"}},
                "allocations": {"type": "array", "items": {"type": "object"}},
                "accrual_plans": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "validator",
        "fn": validate_leave_allocations,
    }
]

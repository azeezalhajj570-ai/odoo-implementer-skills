"""
Migration Plan Validator Tool

Validates a migration plan checklist and detects missing steps
such as backup, staging, rollback, and validation.
"""

from typing import Any, Dict, List, Optional


def validate_migration_plan(plan: Optional[dict] = None,
                            steps: Optional[List[str]] = None) -> dict:
    """
    Validate a migration plan for required steps.

    Args:
        plan: Dict describing the migration plan
        steps: List of planned step names

    Returns:
        Validation results with missing steps and recommendations
    """
    required_steps = {
        "backup",
        "compatibility_analysis",
        "staging_environment",
        "migration_scripts",
        "upgrade_execution",
        "validation",
        "rollback_plan",
    }

    results = {
        "valid": True,
        "missing_steps": [],
        "warnings": [],
        "recommendations": [],
    }

    provided = set()
    if plan:
        provided.update(plan.get("steps", []))
    if steps:
        provided.update(steps)

    missing = required_steps - provided
    if missing:
        results["valid"] = False
        results["missing_steps"] = sorted(missing)
        results["recommendations"].append(
            f"Add missing steps: {', '.join(sorted(missing))}"
        )

    if plan:
        target = plan.get("target_version")
        source = plan.get("source_version")
        if not source or not target:
            results["warnings"].append(
                "Plan should specify source_version and target_version."
            )

    if not results["missing_steps"]:
        results["recommendations"].append(
            "All required steps are present. Document timings and owners for each step."
        )

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="validate_migration_plan",
        description="Validate migration plan for required steps",
        parameters={
            "type": "object",
            "properties": {
                "plan": {
                    "type": "object",
                    "description": "Migration plan with steps"
                },
                "steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of step names"
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_migration",
        category="validator",
        fn=validate_migration_plan,
    ))


tools = [
    {
        "name": "validate_migration_plan",
        "description": "Validate migration plan for required steps",
        "parameters": {
            "type": "object",
            "properties": {
                "plan": {"type": "object"},
                "steps": {"type": "array", "items": {"type": "string"}}
            }
        },
        "category": "validator",
        "fn": validate_migration_plan,
    }
]

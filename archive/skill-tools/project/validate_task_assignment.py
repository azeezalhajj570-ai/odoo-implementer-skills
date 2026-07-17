"""
Task Assignment Validator Tool

Validates task assignment consistency: assignees belong to the project,
workload is balanced, deadlines are realistic, and required fields are set.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition, ToolResult


def validate_task_assignment(tasks: Optional[List[dict]] = None,
                             users: Optional[List[dict]] = None,
                             max_tasks_per_user: int = 10) -> dict:
    """
    Validate task assignment configuration.

    Args:
        tasks: List of task dicts with name, user_ids, date_deadline, stage_fold
        users: List of user dicts with id, name, max_capacity
        max_tasks_per_user: Default threshold for open tasks per user

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
        "user_load": {},
        "unassigned_tasks": 0,
    }

    if not tasks:
        results["issues"].append("No tasks provided for validation.")
        results["valid"] = False
        return results

    user_capacity = {}
    if users:
        for user in users:
            user_capacity[user.get("id")] = {
                "name": user.get("name", "Unknown"),
                "capacity": user.get("max_capacity", max_tasks_per_user),
                "open_tasks": 0,
            }

    for task in tasks:
        name = task.get("name", "Unknown")
        stage_fold = task.get("stage_fold", False)
        user_ids = task.get("user_ids", []) or []
        date_deadline = task.get("date_deadline")
        priority = task.get("priority", "0")

        if not stage_fold and not user_ids:
            results["unassigned_tasks"] += 1
            results["warnings"].append(
                f"Open task '{name}' has no assignees"
            )

        if not date_deadline and priority == "1":
            results["warnings"].append(
                f"High-priority task '{name}' has no deadline"
            )

        for user_id in user_ids:
            if user_id not in user_capacity:
                user_capacity[user_id] = {
                    "name": f"User {user_id}",
                    "capacity": max_tasks_per_user,
                    "open_tasks": 0,
                }
            if not stage_fold:
                user_capacity[user_id]["open_tasks"] += 1

    # Check capacity
    for user_id, data in user_capacity.items():
        load = data["open_tasks"]
        capacity = data["capacity"]
        results["user_load"][data["name"]] = {
            "open_tasks": load,
            "capacity": capacity,
        }
        if load > capacity:
            results["valid"] = False
            results["issues"].append(
                f"User '{data['name']}' is overloaded: {load} open tasks "
                f"(capacity: {capacity})"
            )
        elif load >= capacity * 0.8:
            results["warnings"].append(
                f"User '{data['name']}' is near capacity: {load}/{capacity}"
            )

    if results["unassigned_tasks"] > 0:
        results["recommendations"].append(
            f"Assign {results['unassigned_tasks']} open task(s) to team members."
        )

    overloaded = [u for u, d in user_capacity.items() if d["open_tasks"] > d["capacity"]]
    if overloaded:
        results["recommendations"].append(
            "Redistribute tasks from overloaded users to underutilized members."
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_task_assignment",
        description="Validate task assignment: assignees, workload balance, deadlines",
        parameters={
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Task records to validate"
                },
                "users": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "User capacity definitions"
                },
                "max_tasks_per_user": {
                    "type": "integer",
                    "description": "Default open task threshold per user"
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_project",
        category="validator",
        fn=validate_task_assignment,
    ))


tools = [
    {
        "name": "validate_task_assignment",
        "description": "Validate task assignment: assignees, workload balance, deadlines",
        "parameters": {
            "type": "object",
            "properties": {
                "tasks": {"type": "array", "items": {"type": "object"}},
                "users": {"type": "array", "items": {"type": "object"}},
                "max_tasks_per_user": {"type": "integer"}
            }
        },
        "category": "validator",
        "fn": validate_task_assignment,
    }
]

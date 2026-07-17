"""
Project Health Analyzer Tool

Analyzes a project or set of tasks and returns insights about
progress, overdue work, workload distribution, and bottlenecks.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_project_health(project_data: Optional[dict] = None,
                           task_ids: Optional[List[int]] = None,
                           db_connection: Optional[str] = None) -> dict:
    """
    Analyze project health based on task data and configuration.

    Args:
        project_data: Dict with project summary and task list
        task_ids: List of task IDs to analyze (simulated)
        db_connection: Optional database connection string

    Returns:
        Analysis results with progress, issues, and recommendations
    """
    results = {
        "task_count": 0,
        "open_tasks": 0,
        "done_tasks": 0,
        "blocked_tasks": 0,
        "overdue_tasks": 0,
        "progress_pct": 0.0,
        "issues": [],
        "recommendations": [],
    }

    if project_data:
        tasks = project_data.get("tasks", [])
        results["task_count"] = len(tasks)

        for task in tasks:
            stage_fold = task.get("stage_fold", False)
            kanban_state = task.get("kanban_state", "normal")
            date_deadline = task.get("date_deadline")
            is_overdue = task.get("is_overdue", False)

            if stage_fold:
                results["done_tasks"] += 1
            else:
                results["open_tasks"] += 1

            if kanban_state == "blocked":
                results["blocked_tasks"] += 1
                results["issues"].append(
                    f"Task '{task.get('name', 'Unknown')}' is blocked"
                )

            if is_overdue and not stage_fold:
                results["overdue_tasks"] += 1
                results["issues"].append(
                    f"Task '{task.get('name', 'Unknown')}' is overdue "
                    f"(deadline: {date_deadline})"
                )

        total = results["task_count"]
        if total > 0:
            results["progress_pct"] = round(
                (results["done_tasks"] / total) * 100, 2
            )

        # Generate recommendations
        if results["blocked_tasks"] > 0:
            results["recommendations"].append(
                f"{results['blocked_tasks']} task(s) are blocked. "
                "Review blockers and assign an owner to unblock them."
            )
        if results["overdue_tasks"] > 0:
            results["recommendations"].append(
                f"{results['overdue_tasks']} task(s) are overdue. "
                "Re-prioritize or update deadlines."
            )
        if results["progress_pct"] < 25 and total > 5:
            results["recommendations"].append(
                "Project progress is below 25%. Verify scope and resource allocation."
            )
        if total == 0:
            results["recommendations"].append(
                "No tasks found. Add tasks to begin tracking project health."
            )

    if task_ids:
        results["task_ids_analyzed"] = len(task_ids)

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_project_health",
        description="Analyze project health: progress, overdue tasks, blockers, and recommendations",
        parameters={
            "type": "object",
            "properties": {
                "project_data": {
                    "type": "object",
                    "description": "Project configuration with tasks list"
                },
                "task_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Task IDs to analyze"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Health analysis with progress, issues, and recommendations"
        },
        skill_id="skill_project",
        category="analyzer",
        fn=analyze_project_health,
    ))


tools = [
    {
        "name": "analyze_project_health",
        "description": "Analyze project health: progress, overdue tasks, blockers, and recommendations",
        "parameters": {
            "type": "object",
            "properties": {
                "project_data": {"type": "object"},
                "task_ids": {"type": "array", "items": {"type": "integer"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_project_health,
    }
]

"""
HR Org Structure Analyzer Tool

Analyzes HR department and employee hierarchy, detecting orphaned
employees, missing managers, and department coverage gaps.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_org_structure(departments: Optional[List[dict]] = None,
                          employees: Optional[List[dict]] = None,
                          db_connection: Optional[str] = None) -> dict:
    """
    Analyze HR organizational structure.

    Args:
        departments: List of department dicts with id, name, manager_id, parent_id
        employees: List of employee dicts with id, name, department_id, parent_id
        db_connection: Optional database connection string

    Returns:
        Analysis results with hierarchy stats and issues
    """
    results = {
        "department_count": 0,
        "employee_count": 0,
        "departments_without_manager": [],
        "employees_without_department": [],
        "orphaned_managers": [],
        "issues": [],
        "recommendations": [],
    }

    if departments:
        results["department_count"] = len(departments)
        dept_ids = {d.get("id") for d in departments}
        for dept in departments:
            if not dept.get("manager_id"):
                results["departments_without_manager"].append(dept.get("name"))
            parent_id = dept.get("parent_id")
            if parent_id and parent_id not in dept_ids:
                results["issues"].append(
                    f"Department '{dept.get('name')}' references missing parent {parent_id}"
                )

    if employees:
        results["employee_count"] = len(employees)
        emp_ids = {e.get("id") for e in employees}
        for emp in employees:
            if not emp.get("department_id"):
                results["employees_without_department"].append(emp.get("name"))
            manager_id = emp.get("parent_id")
            if manager_id and manager_id not in emp_ids:
                results["orphaned_managers"].append(
                    f"Employee '{emp.get('name')}' references missing manager {manager_id}"
                )

    if results["departments_without_manager"]:
        results["recommendations"].append(
            "Assign managers to all departments for approval workflows."
        )
    if results["employees_without_department"]:
        results["recommendations"].append(
            "Assign employees to departments for reporting and access control."
        )

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_org_structure",
        description="Analyze HR department and employee hierarchy for gaps",
        parameters={
            "type": "object",
            "properties": {
                "departments": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Department records"
                },
                "employees": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Employee records"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Hierarchy analysis with issues and recommendations"
        },
        skill_id="skill_hr",
        category="analyzer",
        fn=analyze_org_structure,
    ))


tools = [
    {
        "name": "analyze_org_structure",
        "description": "Analyze HR department and employee hierarchy for gaps",
        "parameters": {
            "type": "object",
            "properties": {
                "departments": {"type": "array", "items": {"type": "object"}},
                "employees": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_org_structure,
    }
]

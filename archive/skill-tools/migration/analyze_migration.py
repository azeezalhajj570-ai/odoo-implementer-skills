"""
Migration Compatibility Analyzer Tool

Analyzes a migration scenario (source version, target version, modules)
and returns a compatibility assessment with breaking changes and recommendations.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


BREAKING_CHANGES = {
    "17.0": {
        "18.0": [
            "QWeb t-esc changed default escaping behavior",
            "OWL 2.x lifecycle changes",
        ],
        "19.0": [
            "Odoo 19 ORM constraints use models.Constraint",
            "Index definitions use models.Index",
            "Some legacy widget attributes removed",
        ],
    },
    "18.0": {
        "19.0": [
            "Odoo 19 ORM constraints use models.Constraint",
            "Index definitions use models.Index",
        ],
    },
}


def analyze_migration(source_version: str,
                      target_version: str,
                      modules: Optional[List[str]] = None,
                      custom_modules: Optional[List[str]] = None) -> dict:
    """
    Analyze migration compatibility between Odoo versions.

    Args:
        source_version: Source Odoo version (e.g., '17.0')
        target_version: Target Odoo version (e.g., '19.0')
        modules: List of standard/OCA modules to migrate
        custom_modules: List of custom modules to assess

    Returns:
        Analysis results with breaking changes, risks, and recommendations
    """
    results = {
        "source_version": source_version,
        "target_version": target_version,
        "modules": modules or [],
        "custom_modules": custom_modules or [],
        "breaking_changes": [],
        "risks": [],
        "recommendations": [],
        "valid": True,
    }

    changes = BREAKING_CHANGES.get(source_version, {}).get(target_version, [])
    results["breaking_changes"] = changes

    if not changes:
        results["recommendations"].append(
            "No pre-defined breaking changes for this path. "
            "Perform manual source code review."
        )

    if custom_modules:
        results["recommendations"].append(
            f"Review {len(custom_modules)} custom modules for API changes, "
            "removed fields, and view compatibility."
        )

    if modules:
        results["recommendations"].append(
            f"Verify OpenUpgrade coverage for {len(modules)} modules."
        )

    if source_version == target_version:
        results["valid"] = False
        results["risks"].append("Source and target versions are identical.")

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_migration",
        description="Analyze migration compatibility between Odoo versions",
        parameters={
            "type": "object",
            "properties": {
                "source_version": {
                    "type": "string",
                    "description": "Source Odoo version"
                },
                "target_version": {
                    "type": "string",
                    "description": "Target Odoo version"
                },
                "modules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Modules to migrate"
                },
                "custom_modules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Custom modules to assess"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Compatibility analysis results"
        },
        skill_id="skill_migration",
        category="analyzer",
        fn=analyze_migration,
    ))


tools = [
    {
        "name": "analyze_migration",
        "description": "Analyze migration compatibility between Odoo versions",
        "parameters": {
            "type": "object",
            "properties": {
                "source_version": {"type": "string"},
                "target_version": {"type": "string"},
                "modules": {"type": "array", "items": {"type": "string"}},
                "custom_modules": {"type": "array", "items": {"type": "string"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_migration,
    }
]

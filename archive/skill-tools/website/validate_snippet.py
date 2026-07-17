"""
Website Snippet Validator Tool

Validates a snippet definition for required attributes and structure.
"""

import logging
from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition

logger = logging.getLogger(__name__)


def validate_snippet(snippet_data: Optional[dict] = None,
                     require_thumbnail: bool = True) -> dict:
    """
    Validate a website snippet definition.

    Args:
        snippet_data: Dict with snippet XML/arch content
        require_thumbnail: Whether a t-thumbnail attribute is required

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if not snippet_data:
        results["issues"].append("No snippet data provided")
        results["valid"] = False
        return results

    arch = snippet_data.get("arch", "")
    name = snippet_data.get("name", "Unnamed snippet")

    if not name:
        results["issues"].append("Snippet is missing a name")
        results["valid"] = False

    if "t-snippet" not in arch:
        results["issues"].append("Snippet is missing t-snippet attribute")
        results["valid"] = False

    if require_thumbnail and "t-thumbnail" not in arch:
        results["warnings"].append("Snippet is missing t-thumbnail preview image")

    if not snippet_data.get("view_id"):
        results["warnings"].append("Snippet is not linked to an ir.ui.view record")

    if len(arch) < 50:
        results["issues"].append("Snippet content appears too short to be useful")
        results["valid"] = False

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_snippet",
        description="Validate a website snippet definition",
        parameters={
            "type": "object",
            "properties": {
                "snippet_data": {
                    "type": "object",
                    "description": "Snippet dictionary with arch and metadata"
                },
                "require_thumbnail": {
                    "type": "boolean",
                    "description": "Require t-thumbnail attribute",
                    "default": True
                }
            }
        },
        returns={"type": "object", "description": "Snippet validation results"},
        skill_id="skill_website",
        category="validator",
        fn=validate_snippet,
    ))


tools = [
    {
        "name": "validate_snippet",
        "description": "Validate a website snippet definition",
        "parameters": {
            "type": "object",
            "properties": {
                "snippet_data": {"type": "object"},
                "require_thumbnail": {"type": "boolean"}
            }
        },
        "category": "validator",
        "fn": validate_snippet,
    }
]

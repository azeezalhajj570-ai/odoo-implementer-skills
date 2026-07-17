"""
Odoo Module Analyzer Tool

Analyzes a module directory structure or manifest and reports
missing files, common issues, and recommendations.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


EXPECTED_FILES = [
    "__manifest__.py",
    "__init__.py",
    "models/__init__.py",
    "security/ir.model.access.csv",
]


def analyze_module(manifest: Optional[dict] = None,
                   files: Optional[List[str]] = None,
                   module_name: Optional[str] = None) -> dict:
    """
    Analyze an Odoo module structure.

    Args:
        manifest: Parsed __manifest__.py content
        files: List of relative file paths in the module
        module_name: Technical name of the module

    Returns:
        Analysis results with issues and recommendations
    """
    results = {
        "module_name": module_name,
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if not manifest:
        results["issues"].append("Missing or empty __manifest__.py")
        results["valid"] = False
        return results

    required_keys = ["name", "version", "depends", "installable"]
    for key in required_keys:
        if key not in manifest:
            results["issues"].append(f"Missing manifest key: {key}")
            results["valid"] = False

    if "depends" in manifest and "base" not in manifest["depends"]:
        results["warnings"].append("Module does not depend on base.")

    if files:
        file_set = set(files)
        for expected in EXPECTED_FILES:
            if expected not in file_set:
                results["warnings"].append(f"Missing recommended file: {expected}")

        if any("models/" in f for f in files):
            if "models/__init__.py" not in file_set:
                results["issues"].append("models/ exists but models/__init__.py is missing")
                results["valid"] = False

    results["recommendations"].append(
        "Ensure all XML data files are listed in manifest 'data' section."
    )

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_module",
        description="Analyze Odoo module structure and manifest",
        parameters={
            "type": "object",
            "properties": {
                "manifest": {
                    "type": "object",
                    "description": "Parsed __manifest__.py content"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Relative file paths in module"
                },
                "module_name": {
                    "type": "string",
                    "description": "Technical module name"
                }
            }
        },
        returns={"type": "object", "description": "Module analysis results"},
        skill_id="skill_development",
        category="analyzer",
        fn=analyze_module,
    ))


tools = [
    {
        "name": "analyze_module",
        "description": "Analyze Odoo module structure and manifest",
        "parameters": {
            "type": "object",
            "properties": {
                "manifest": {"type": "object"},
                "files": {"type": "array", "items": {"type": "string"}},
                "module_name": {"type": "string"}
            }
        },
        "category": "analyzer",
        "fn": analyze_module,
    }
]

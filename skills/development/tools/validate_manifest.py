"""
Manifest Validator Tool

Validates an Odoo module manifest for required keys, version format,
dependencies, and data file consistency.
"""

import re
from typing import Any, Dict, List, Optional


VERSION_RE = re.compile(r"^\d+\.0\.\d+\.\d+\.\d+$")


def validate_manifest(manifest: Optional[dict] = None,
                      data_files: Optional[List[str]] = None,
                      existing_files: Optional[List[str]] = None) -> dict:
    """
    Validate an Odoo module manifest.

    Args:
        manifest: Parsed __manifest__.py content
        data_files: Files declared in manifest 'data' or 'demo'
        existing_files: Files that actually exist in the module

    Returns:
        Validation results with issues and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if not manifest:
        results["issues"].append("Manifest is empty")
        results["valid"] = False
        return results

    required_keys = ["name", "version", "depends", "installable"]
    for key in required_keys:
        if key not in manifest:
            results["issues"].append(f"Missing required key: {key}")
            results["valid"] = False

    version = manifest.get("version", "")
    if version and not VERSION_RE.match(version):
        results["warnings"].append(
            f"Version '{version}' does not match Odoo module format major.0.x.y.z"
        )

    if "base" not in manifest.get("depends", []):
        results["issues"].append("Module must depend on base")
        results["valid"] = False

    if data_files and existing_files:
        missing_files = set(data_files) - set(existing_files)
        if missing_files:
            results["warnings"].append(
                f"Files declared in manifest but not found: {sorted(missing_files)}"
            )

    if not manifest.get("license"):
        results["recommendations"].append(
            "Add a 'license' key to the manifest for clarity."
        )

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="validate_manifest",
        description="Validate Odoo module manifest",
        parameters={
            "type": "object",
            "properties": {
                "manifest": {
                    "type": "object",
                    "description": "Parsed __manifest__.py content"
                },
                "data_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files declared in manifest data/demo"
                },
                "existing_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files that exist in module"
                }
            }
        },
        returns={"type": "object", "description": "Manifest validation results"},
        skill_id="skill_development",
        category="validator",
        fn=validate_manifest,
    ))


tools = [
    {
        "name": "validate_manifest",
        "description": "Validate Odoo module manifest",
        "parameters": {
            "type": "object",
            "properties": {
                "manifest": {"type": "object"},
                "data_files": {"type": "array", "items": {"type": "string"}},
                "existing_files": {"type": "array", "items": {"type": "string"}}
            }
        },
        "category": "validator",
        "fn": validate_manifest,
    }
]

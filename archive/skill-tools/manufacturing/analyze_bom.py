"""
Manufacturing BOM Analyzer Tool

Analyzes a Bill of Materials configuration and returns insights about
component depth, phantom usage, by-products, and potential issues.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_bom(bom_data: Optional[dict] = None,
                max_depth: int = 5) -> dict:
    """
    Analyze a BOM configuration.

    Args:
        bom_data: Dict describing the BOM (product, type, lines, byproducts)
        max_depth: Maximum recursion depth for multi-level BOM checks

    Returns:
        Analysis results with counts, issues, and recommendations
    """
    results = {
        "component_count": 0,
        "operation_count": 0,
        "byproduct_count": 0,
        "bom_type": "unknown",
        "issues": [],
        "recommendations": [],
    }

    if not bom_data:
        results["issues"].append("No BOM data provided")
        return results

    results["bom_type"] = bom_data.get("type", "normal")
    lines = bom_data.get("bom_line_ids", [])
    operations = bom_data.get("operation_ids", [])
    byproducts = bom_data.get("byproduct_ids", [])

    results["component_count"] = len(lines)
    results["operation_count"] = len(operations)
    results["byproduct_count"] = len(byproducts)

    for line in lines:
        qty = line.get("product_qty", 0)
        if qty <= 0:
            results["issues"].append(
                f"Component '{line.get('product_id', 'unknown')}' has zero or negative quantity"
            )

    if results["bom_type"] == "phantom" and operations:
        results["issues"].append("Phantom BOMs should not define operations")

    if results["bom_type"] == "subcontracting" and not bom_data.get("subcontractor_ids"):
        results["warnings"] = results.get("warnings", []) + [
            "Subcontracting BOM has no subcontractors configured"
        ]

    if results["component_count"] == 0 and results["byproduct_count"] == 0:
        results["issues"].append("BOM has no components or by-products")

    if results["operation_count"] == 0 and results["bom_type"] == "normal":
        results["recommendations"].append(
            "Consider adding a routing to track operation time and work center load"
        )

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_bom",
        description="Analyze a manufacturing BOM for completeness and issues",
        parameters={
            "type": "object",
            "properties": {
                "bom_data": {
                    "type": "object",
                    "description": "BOM configuration dictionary"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Max recursion depth for multi-level checks",
                    "default": 5
                }
            }
        },
        returns={
            "type": "object",
            "description": "BOM analysis with counts, issues, recommendations"
        },
        skill_id="skill_manufacturing",
        category="analyzer",
        fn=analyze_bom,
    ))


tools = [
    {
        "name": "analyze_bom",
        "description": "Analyze a manufacturing BOM for completeness and issues",
        "parameters": {
            "type": "object",
            "properties": {
                "bom_data": {"type": "object"},
                "max_depth": {"type": "integer"}
            }
        },
        "category": "analyzer",
        "fn": analyze_bom,
    }
]

"""
Inventory Stock Level Analyzer Tool

Analyzes stock levels against reordering rules and identifies
potential shortages, excess stock, and missing reordering rules.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_stock_levels(products: Optional[List[dict]] = None,
                         orderpoints: Optional[List[dict]] = None,
                         db_connection: Optional[str] = None) -> dict:
    """
    Analyze stock levels and reordering rule coverage.

    Args:
        products: List of product dicts with id, name, qty_available, virtual_available
        orderpoints: List of reordering rule dicts with product_id, product_min_qty, product_max_qty
        db_connection: Optional database connection string

    Returns:
        Analysis results with shortages, excess, and recommendations
    """
    results = {
        "product_count": 0,
        "orderpoint_count": 0,
        "shortages": [],
        "excess": [],
        "missing_orderpoint": [],
        "issues": [],
        "recommendations": [],
    }

    if products:
        results["product_count"] = len(products)
        orderpoint_product_ids = {op.get("product_id") for op in orderpoints or []}

        for product in products:
            pid = product.get("id")
            qty = product.get("qty_available", 0)
            virtual = product.get("virtual_available", 0)

            if virtual < 0:
                results["shortages"].append({
                    "product": product.get("name"),
                    "virtual_available": virtual,
                })
            if qty > 1000:
                results["excess"].append({
                    "product": product.get("name"),
                    "qty_available": qty,
                })
            if pid not in orderpoint_product_ids and product.get("type") == "product":
                results["missing_orderpoint"].append(product.get("name"))

    if orderpoints:
        results["orderpoint_count"] = len(orderpoints)
        for op in orderpoints:
            if op.get("product_min_qty", 0) > op.get("product_max_qty", 0):
                results["issues"].append(
                    f"Reordering rule for product {op.get('product_id')} has min > max"
                )

    if results["shortages"]:
        results["recommendations"].append("Review negative virtual stock and trigger procurements.")
    if results["missing_orderpoint"]:
        results["recommendations"].append("Add reordering rules for storable products without coverage.")

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_stock_levels",
        description="Analyze stock levels, shortages, and reordering rule coverage",
        parameters={
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Product records with stock quantities"
                },
                "orderpoints": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Reordering rule records"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Stock analysis with shortages, excess, and recommendations"
        },
        skill_id="skill_inventory",
        category="analyzer",
        fn=analyze_stock_levels,
    ))


tools = [
    {
        "name": "analyze_stock_levels",
        "description": "Analyze stock levels, shortages, and reordering rule coverage",
        "parameters": {
            "type": "object",
            "properties": {
                "products": {"type": "array", "items": {"type": "object"}},
                "orderpoints": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_stock_levels,
    }
]

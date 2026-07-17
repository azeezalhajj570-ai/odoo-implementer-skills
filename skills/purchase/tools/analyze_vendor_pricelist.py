"""
Purchase Vendor Pricelist Analyzer Tool

Analyzes vendor pricing data and detects missing suppliers, price gaps,
and opportunities for cost savings.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_vendor_pricelist(product_id: Optional[int] = None,
                               supplierinfo: Optional[List[dict]] = None,
                               currency_id: Optional[int] = None) -> dict:
    """
    Analyze vendor pricelist data for a product or set of supplierinfo records.

    Args:
        product_id: Product ID being analyzed
        supplierinfo: List of supplierinfo dicts (partner_id, min_qty, price, currency_id)
        currency_id: Optional currency to normalize prices

    Returns:
        Analysis results with best price, issues, and recommendations
    """
    results = {
        "product_id": product_id,
        "vendor_count": 0,
        "best_price": None,
        "best_vendor": None,
        "issues": [],
        "recommendations": [],
    }

    if not supplierinfo:
        results["issues"].append("No supplierinfo records provided")
        return results

    results["vendor_count"] = len({s.get("partner_id") for s in supplierinfo if s.get("partner_id")})

    valid_prices = []
    for info in supplierinfo:
        price = info.get("price")
        if price is None:
            continue
        valid_prices.append((price, info))

    if valid_prices:
        best_price, best_info = min(valid_prices, key=lambda x: x[0])
        results["best_price"] = best_price
        results["best_vendor"] = best_info.get("partner_id")

    if results["vendor_count"] == 0:
        results["issues"].append("No vendors configured for the product")
    elif results["vendor_count"] == 1:
        results["recommendations"].append("Consider adding a second vendor for price competition")

    min_qty_values = [s.get("min_qty", 0) for s in supplierinfo if s.get("min_qty") is not None]
    if min_qty_values and min(min_qty_values) > 1:
        results["recommendations"].append("Add a supplierinfo line with min_qty=1 for small orders")

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_vendor_pricelist",
        description="Analyze vendor pricelist configuration for a product",
        parameters={
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "integer",
                    "description": "Product ID"
                },
                "supplierinfo": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Supplierinfo records"
                },
                "currency_id": {
                    "type": "integer",
                    "description": "Currency ID to normalize prices"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Pricelist analysis with best price and recommendations"
        },
        skill_id="skill_purchase",
        category="analyzer",
        fn=analyze_vendor_pricelist,
    ))


tools = [
    {
        "name": "analyze_vendor_pricelist",
        "description": "Analyze vendor pricelist configuration for a product",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "supplierinfo": {"type": "array", "items": {"type": "object"}},
                "currency_id": {"type": "integer"}
            }
        },
        "category": "analyzer",
        "fn": analyze_vendor_pricelist,
    }
]

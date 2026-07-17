"""
E-commerce Product Catalog Analyzer Tool

Analyzes a product catalog configuration or list of product records and returns
insights about publication status, categorization, pricing, variants, and SEO.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_product_catalog(products: Optional[List[dict]] = None,
                            categories: Optional[List[dict]] = None,
                            db_connection: Optional[str] = None) -> dict:
    """
    Analyze an e-commerce product catalog.

    Args:
        products: List of product dicts with name, is_published, public_categ_ids,
                  list_price, has_image, has_variants, meta_title, meta_description.
        categories: List of public category dicts with name, parent_id, sequence.
        db_connection: Optional database connection string.

    Returns:
        Analysis results with counts, issues, and recommendations.
    """
    results = {
        "product_count": 0,
        "published_count": 0,
        "unpublished_count": 0,
        "category_count": 0,
        "root_category_count": 0,
        "issues": [],
        "recommendations": [],
    }

    if not products and not categories:
        results["issues"].append("No products or categories provided")
        return results

    if products:
        results["product_count"] = len(products)

        for product in products:
            is_published = product.get("is_published", False)
            categories_ids = product.get("public_categ_ids", []) or []
            has_image = product.get("has_image", False)
            meta_title = product.get("meta_title", "")
            meta_description = product.get("meta_description", "")
            list_price = product.get("list_price", 0.0)

            if is_published:
                results["published_count"] += 1
            else:
                results["unpublished_count"] += 1

            if is_published and not categories_ids:
                results["issues"].append(
                    f"Product '{product.get('name')}' is published but has no public categories"
                )

            if is_published and not has_image:
                results["recommendations"].append(
                    f"Product '{product.get('name')}' has no image; add one to improve conversion"
                )

            if is_published and list_price <= 0:
                results["issues"].append(
                    f"Product '{product.get('name')}' is published with price {list_price}"
                )

            if is_published and (not meta_title or not meta_description):
                results["recommendations"].append(
                    f"Product '{product.get('name')}' is missing SEO meta title or description"
                )

        if results["published_count"] == 0 and results["product_count"] > 0:
            results["issues"].append("No products are published on the website")

        unpublished_ratio = results["unpublished_count"] / max(results["product_count"], 1)
        if unpublished_ratio > 0.5:
            results["recommendations"].append(
                f"{unpublished_ratio:.0%} of products are unpublished; review visibility settings"
            )

    if categories:
        results["category_count"] = len(categories)
        results["root_category_count"] = sum(
            1 for cat in categories if not cat.get("parent_id")
        )

        for category in categories:
            if not category.get("name"):
                results["issues"].append("Found a public category without a name")

        if results["root_category_count"] == 0 and results["category_count"] > 0:
            results["issues"].append("No root categories found; navigation may be broken")

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_product_catalog",
        description="Analyze e-commerce product catalog for publication, categorization, pricing, and SEO issues",
        parameters={
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of product dictionaries"
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of public category dictionaries"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Catalog analysis with counts, issues, and recommendations"
        },
        skill_id="skill_ecommerce",
        category="analyzer",
        fn=analyze_product_catalog,
    ))


tools = [
    {
        "name": "analyze_product_catalog",
        "description": "Analyze e-commerce product catalog for publication, categorization, pricing, and SEO issues",
        "parameters": {
            "type": "object",
            "properties": {
                "products": {"type": "array", "items": {"type": "object"}},
                "categories": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_product_catalog,
    }
]

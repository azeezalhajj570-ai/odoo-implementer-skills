"""
Website SEO Analyzer Tool

Analyzes a website page or set of pages for SEO completeness and issues.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_website_seo(pages: Optional[List[dict]] = None) -> dict:
    """
    Analyze website pages for SEO metadata completeness.

    Args:
        pages: List of page dicts with title, meta_description, url, is_published

    Returns:
        SEO analysis with issues and recommendations
    """
    results = {
        "page_count": 0,
        "published_count": 0,
        "issues": [],
        "recommendations": [],
    }

    if not pages:
        results["issues"].append("No pages provided")
        return results

    results["page_count"] = len(pages)

    for page in pages:
        title = page.get("title", "")
        description = page.get("meta_description", "")
        url = page.get("url", "")
        is_published = page.get("is_published", False)

        if is_published:
            results["published_count"] += 1

        if not title:
            results["issues"].append(f"Page {url}: missing title")
        elif len(title) > 60:
            results["recommendations"].append(f"Page {url}: title exceeds 60 characters")

        if not description:
            results["issues"].append(f"Page {url}: missing meta description")
        elif len(description) > 160:
            results["recommendations"].append(f"Page {url}: meta description exceeds 160 characters")

        if not re.match(r"^[a-z0-9/_-]+$", url.strip("/")):
            results["issues"].append(f"Page {url}: URL contains non-SEO-friendly characters")

        if not is_published:
            results["recommendations"].append(f"Page {url}: not published, will not appear in sitemap")

    return results


def register(registry):
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_website_seo",
        description="Analyze website pages for SEO completeness",
        parameters={
            "type": "object",
            "properties": {
                "pages": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of page dictionaries"
                }
            }
        },
        returns={
            "type": "object",
            "description": "SEO analysis with issues and recommendations"
        },
        skill_id="skill_website",
        category="analyzer",
        fn=analyze_website_seo,
    ))


tools = [
    {
        "name": "analyze_website_seo",
        "description": "Analyze website pages for SEO completeness",
        "parameters": {
            "type": "object",
            "properties": {
                "pages": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_website_seo,
    }
]

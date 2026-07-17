"""
Social Posts Analyzer Tool

Analyzes a collection of social.post records and returns insights
about platform distribution, state, scheduling, media usage, and campaigns.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_social_posts(posts_data: Optional[List[dict]] = None,
                         account_data: Optional[List[dict]] = None,
                         db_connection: Optional[str] = None) -> dict:
    """
    Analyze social posts configuration and content.

    Args:
        posts_data: List of dicts representing social.post records
        account_data: Optional list of social.account records for mapping
        db_connection: Optional database connection string

    Returns:
        Analysis results with platform distribution, state counts,
        scheduling overview, media stats, campaign coverage, issues
    """
    results = {
        "post_count": 0,
        "state_counts": {},
        "platform_counts": {},
        "scheduled_count": 0,
        "posted_count": 0,
        "failed_count": 0,
        "draft_count": 0,
        "with_media": 0,
        "with_campaign": 0,
        "with_ai_content": 0,
        "recommendations": [],
        "issues": [],
    }

    if not posts_data:
        results["recommendations"].append(
            "No post data provided. Pass a list of social.post dicts to analyze."
        )
        return results

    results["post_count"] = len(posts_data)
    account_map = {}
    if account_data:
        account_map = {a.get("id"): a.get("media_type", "unknown") for a in account_data}

    for post in posts_data:
        state = post.get("state", "draft")
        results["state_counts"][state] = results["state_counts"].get(state, 0) + 1

        if state == "scheduled":
            results["scheduled_count"] += 1
        elif state == "posted":
            results["posted_count"] += 1
        elif state == "failed":
            results["failed_count"] += 1
        elif state == "draft":
            results["draft_count"] += 1

        # Platform distribution from account_ids
        account_ids = post.get("account_ids", [])
        if isinstance(account_ids, list):
            for account_id in account_ids:
                media = account_map.get(account_id, "unknown")
                results["platform_counts"][media] = results["platform_counts"].get(media, 0) + 1

        # Media and campaign flags
        if post.get("image_ids"):
            results["with_media"] += 1
        if post.get("campaign_id"):
            results["with_campaign"] += 1
        if post.get("is_ai_content"):
            results["with_ai_content"] += 1

    # Generate insights
    if results["failed_count"] > 0:
        results["issues"].append(
            f"{results['failed_count']} post(s) are in failed state. "
            "Review live post errors and account tokens."
        )

    if results["scheduled_count"] > 0 and not any(p.get("scheduled_date") for p in posts_data):
        results["issues"].append(
            "Scheduled posts found without scheduled_date values."
        )

    if results["with_campaign"] < results["post_count"] / 2:
        results["recommendations"].append(
            "Many posts are not linked to a UTM campaign. "
            "Link posts to campaigns for better attribution."
        )

    if results["with_media"] < results["post_count"] / 2:
        results["recommendations"].append(
            "Consider adding images or videos to more posts to improve engagement."
        )

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_social_posts",
        description="Analyze social posts for platform distribution, state, scheduling, media, and campaigns",
        parameters={
            "type": "object",
            "properties": {
                "posts_data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of social.post dicts"
                },
                "account_data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional social.account mapping"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Analysis with counts, issues, and recommendations"
        },
        skill_id="skill_social_marketing",
        category="analyzer",
        fn=analyze_social_posts,
    ))


tools = [
    {
        "name": "analyze_social_posts",
        "description": "Analyze social posts for platform distribution, state, scheduling, media, and campaigns",
        "parameters": {
            "type": "object",
            "properties": {
                "posts_data": {"type": "array", "items": {"type": "object"}},
                "account_data": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_social_posts,
    }
]

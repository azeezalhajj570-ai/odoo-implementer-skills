"""
Scheduled Social Post Validator Tool

Validates that a scheduled social.post is ready for publication.
Checks message length, media, account/page linkage, scheduled_date,
and platform-specific constraints.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Platform-specific limits (text and media) for validation guidance
PLATFORM_LIMITS = {
    "twitter": {"text_max": 280, "media_max": 4},
    "facebook": {"text_max": 63206, "media_max": 10},
    "instagram": {"text_max": 2200, "media_min": 1, "media_max": 10},
    "linkedin": {"text_max": 3000, "media_max": 9},
    "youtube": {"text_max": 5000, "media_min": 1, "media_max": 1},
}


def validate_scheduled_post(post: Optional[dict] = None,
                            accounts: Optional[List[dict]] = None,
                            pages: Optional[List[dict]] = None) -> dict:
    """
    Validate a scheduled social.post for readiness.

    Args:
        post: Dict representing a social.post record
        accounts: Optional list of social.account records
        pages: Optional list of social.page records

    Returns:
        Validation results with valid flag, issues, warnings, and recommendations
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    if not post:
        results["issues"].append("No post data provided.")
        results["valid"] = False
        return results

    state = post.get("state", "draft")
    if state != "scheduled":
        results["warnings"].append(
            f"Post state is '{state}', not 'scheduled'. Validation is meant for scheduled posts."
        )

    scheduled_date = post.get("scheduled_date")
    if not scheduled_date:
        results["issues"].append("scheduled_date is required for a scheduled post.")
        results["valid"] = False
    else:
        try:
            dt = datetime.fromisoformat(str(scheduled_date).replace("Z", "+00:00"))
            if dt <= datetime.now(dt.tzinfo):
                results["issues"].append(
                    "scheduled_date is in the past. The post may be picked up immediately or skipped."
                )
                results["valid"] = False
        except ValueError:
            results["issues"].append("scheduled_date is not a valid ISO datetime.")
            results["valid"] = False

    message = post.get("message", "")
    if not message or not message.strip():
        results["issues"].append("Post message is empty.")
        results["valid"] = False

    account_ids = post.get("account_ids", []) or []
    if not account_ids:
        results["issues"].append("No social accounts selected for publishing.")
        results["valid"] = False

    image_ids = post.get("image_ids", []) or []

    # Platform-specific checks
    account_map = {}
    if accounts:
        account_map = {a.get("id"): a for a in accounts}

    for account_id in account_ids:
        account = account_map.get(account_id)
        if not account:
            results["warnings"].append(
                f"Account {account_id} details not provided; skipping platform checks."
            )
            continue

        media_type = account.get("media_type", "").lower()
        limits = PLATFORM_LIMITS.get(media_type, {})

        if media_type == "youtube" and not image_ids:
            results["issues"].append("YouTube posts require a video attachment.")
            results["valid"] = False

        if media_type == "instagram" and not image_ids:
            results["issues"].append("Instagram posts require an image or video attachment.")
            results["valid"] = False

        text_max = limits.get("text_max")
        if text_max and len(message) > text_max:
            results["issues"].append(
                f"{media_type.title()} text exceeds {text_max} characters."
            )
            results["valid"] = False

        media_max = limits.get("media_max")
        if media_max and len(image_ids) > media_max:
            results["issues"].append(
                f"{media_type.title()} allows at most {media_max} media item(s)."
            )
            results["valid"] = False

    # Campaign linkage recommendation
    if not post.get("campaign_id"):
        results["recommendations"].append(
            "Link the post to a UTM campaign for attribution tracking."
        )

    # AI content recommendation
    if post.get("is_ai_content") and not message:
        results["issues"].append("AI-generated flag is set but message is empty.")
        results["valid"] = False

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="validate_scheduled_post",
        description="Validate a scheduled social.post for readiness to publish",
        parameters={
            "type": "object",
            "properties": {
                "post": {
                    "type": "object",
                    "description": "social.post dict"
                },
                "accounts": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "social.account records"
                },
                "pages": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "social.page records"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Validation results with issues and recommendations"
        },
        skill_id="skill_social_marketing",
        category="validator",
        fn=validate_scheduled_post,
    ))


tools = [
    {
        "name": "validate_scheduled_post",
        "description": "Validate a scheduled social.post for readiness to publish",
        "parameters": {
            "type": "object",
            "properties": {
                "post": {"type": "object"},
                "accounts": {"type": "array", "items": {"type": "object"}},
                "pages": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "validator",
        "fn": validate_scheduled_post,
    }
]

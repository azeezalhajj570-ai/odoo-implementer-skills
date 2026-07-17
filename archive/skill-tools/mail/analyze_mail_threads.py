"""
Mail Thread Analyzer Tool

Analyzes mail.thread usage, message history, followers, and activity coverage
for a record or set of records and returns actionable insights.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_mail_threads(
    record_data: Optional[dict] = None,
    message_ids: Optional[List[int]] = None,
    follower_ids: Optional[List[int]] = None,
    activity_data: Optional[List[dict]] = None,
    db_connection: Optional[str] = None,
) -> dict:
    """
    Analyze a mail thread configuration and message history.

    Args:
        record_data: Dict describing the record (model, res_id, follower_count, etc.)
        message_ids: List of mail.message IDs to analyze (simulated)
        follower_ids: List of mail.followers IDs to analyze (simulated)
        activity_data: List of activity dicts (type, deadline, user_id)
        db_connection: Optional database connection string

    Returns:
        Analysis results with message coverage, follower health, activity gaps,
        and recommendations.
    """
    results = {
        "record": record_data or {},
        "message_count": 0,
        "message_types": {},
        "follower_count": 0,
        "external_follower_count": 0,
        "activity_count": 0,
        "overdue_activity_count": 0,
        "recommendations": [],
        "issues": [],
    }

    if record_data:
        results["follower_count"] = record_data.get("follower_count", 0)
        results["external_follower_count"] = record_data.get("external_follower_count", 0)

    if message_ids:
        results["message_count"] = len(message_ids)

    if activity_data:
        results["activity_count"] = len(activity_data)
        for activity in activity_data:
            if activity.get("is_overdue"):
                results["overdue_activity_count"] += 1

    # Issue checks
    if results["message_count"] == 0 and results["activity_count"] == 0:
        results["issues"].append(
            "Record has no messages or activities. Consider adding a follow-up activity."
        )

    if results["external_follower_count"] == 0 and results["message_count"] > 0:
        results["recommendations"].append(
            "Record has messages but no external followers. Add the customer/partner "
            "as a follower if they should receive updates."
        )

    if results["follower_count"] > 20:
        results["recommendations"].append(
            "Thread has many followers. Review whether all subscribers still need "
            "notifications to reduce noise."
        )

    if results["overdue_activity_count"] > 0:
        results["issues"].append(
            f"{results['overdue_activity_count']} activities are overdue. Reassign or "
            f"complete them."
        )

    if results["activity_count"] == 0:
        results["recommendations"].append(
            "No activities scheduled. Consider scheduling a next step to keep the thread alive."
        )

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_mail_threads",
        description="Analyze mail thread health: messages, followers, activities, overdue items",
        parameters={
            "type": "object",
            "properties": {
                "record_data": {
                    "type": "object",
                    "description": "Record metadata including follower_count and external_follower_count"
                },
                "message_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "mail.message IDs to analyze"
                },
                "follower_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "mail.followers IDs to analyze"
                },
                "activity_data": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Activity dicts with keys type, deadline, user_id, is_overdue"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Thread health analysis with recommendations and issues"
        },
        skill_id="skill_mail",
        category="analyzer",
        fn=analyze_mail_threads,
    ))


tools = [
    {
        "name": "analyze_mail_threads",
        "description": "Analyze mail thread health: messages, followers, activities, overdue items",
        "parameters": {
            "type": "object",
            "properties": {
                "record_data": {"type": "object"},
                "message_ids": {"type": "array", "items": {"type": "integer"}},
                "follower_ids": {"type": "array", "items": {"type": "integer"}},
                "activity_data": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_mail_threads,
    }
]

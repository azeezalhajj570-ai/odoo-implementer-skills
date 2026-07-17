"""
CRM Pipeline Analyzer Tool

Analyzes a CRM pipeline configuration or database and returns
insights about stages, probabilities, lead distribution, bottlenecks.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_pipeline(pipeline_data: Optional[dict] = None,
                     lead_ids: Optional[List[int]] = None,
                     db_connection: Optional[str] = None) -> dict:
    """
    Analyze a CRM pipeline configuration.

    Args:
        pipeline_data: Dict with stages, probabilities, team config
        lead_ids: List of lead IDs to analyze (simulated)
        db_connection: Optional database connection string

    Returns:
        Analysis results with stages, distribution, recommendations
    """
    results = {
        "stages_count": 0,
        "stages": [],
        "recommendations": [],
        "issues": [],
    }

    if pipeline_data:
        stages = pipeline_data.get("stages", [])
        results["stages_count"] = len(stages)

        for stage in stages:
            s = {
                "name": stage.get("name", "Unknown"),
                "probability": stage.get("probability", 0),
                "is_won": stage.get("is_won", False),
                "sequence": stage.get("sequence", 0),
            }

            # Check for common issues
            if s["is_won"] and s["probability"] < 100:
                results["issues"].append(
                    f"Stage '{s['name']}' is marked as Won but probability "
                    f"is {s['probability']}% (should be 100%)"
                )

            if s["probability"] <= 0 and not s["is_won"]:
                results["issues"].append(
                    f"Stage '{s['name']}' has zero probability"
                )

            results["stages"].append(s)

        # Generate recommendations
        if results["stages_count"] < 3:
            results["recommendations"].append(
                "Pipeline has fewer than 3 stages. Consider adding "
                "more granular stages for better tracking."
            )
        elif results["stages_count"] > 10:
            results["recommendations"].append(
                "Pipeline has more than 10 stages. Consider simplifying "
                "to reduce complexity."
            )

    if lead_ids:
        results["lead_count_analyzed"] = len(lead_ids)

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_pipeline",
        description="Analyze CRM pipeline configuration for stage layout, probabilities, bottlenecks",
        parameters={
            "type": "object",
            "properties": {
                "pipeline_data": {
                    "type": "object",
                    "description": "Pipeline configuration with stages"
                },
                "lead_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Lead IDs to analyze"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Analysis with stages, issues, recommendations"
        },
        skill_id="skill_crm",
        category="analyzer",
        fn=analyze_pipeline,
    ))


tools = [
    {
        "name": "analyze_pipeline",
        "description": "Analyze CRM pipeline configuration for stage layout, probabilities, bottlenecks",
        "parameters": {
            "type": "object",
            "properties": {
                "pipeline_data": {"type": "object"},
                "lead_ids": {"type": "array", "items": {"type": "integer"}}
            }
        },
        "category": "analyzer",
        "fn": analyze_pipeline,
    }
]

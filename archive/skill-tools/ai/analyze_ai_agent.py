"""
AI Agent Analyzer Tool

Analyzes an ai.agent configuration and returns insights about
provider/model compatibility, tool setup, security exposure, and
readiness for deployment.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def analyze_ai_agent(agent_data: Optional[dict] = None,
                     agent_id: Optional[int] = None,
                     db_connection: Optional[str] = None) -> dict:
    """
    Analyze an AI agent configuration.

    Args:
        agent_data: Dict describing the ai.agent record
        agent_id: Optional Odoo record ID
        db_connection: Optional database connection string

    Returns:
        Analysis results with issues, warnings, and recommendations
    """
    results = {
        "agent_id": agent_id,
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
        "provider_ready": False,
        "model_ready": False,
        "tool_count": 0,
        "security_score": "unknown",
    }

    if not agent_data:
        results["valid"] = False
        results["issues"].append("No agent_data provided for analysis")
        return results

    name = agent_data.get("name", "Unknown")
    system_prompt = agent_data.get("system_prompt", "")
    welcome_message = agent_data.get("welcome_message", "")
    provider = agent_data.get("provider", {})
    model = agent_data.get("model", {})
    tools = agent_data.get("tools", [])
    visibility = agent_data.get("visibility", "internal")
    memory_enabled = agent_data.get("memory_enabled", False)
    max_history = agent_data.get("max_history", 0)

    results["tool_count"] = len(tools)

    # Provider validation
    if not provider:
        results["issues"].append(f"Agent '{name}' has no provider configured")
        results["valid"] = False
    else:
        provider_type = provider.get("provider_type")
        if not provider_type:
            results["issues"].append("Provider has no provider_type")
            results["valid"] = False
        elif provider_type not in {
            "openai", "anthropic", "azure_openai", "ollama", "groq", "custom"
        }:
            results["warnings"].append(
                f"Unrecognized provider_type '{provider_type}'"
            )
        else:
            results["provider_ready"] = True

    # Model validation
    if not model:
        results["issues"].append(f"Agent '{name}' has no model configured")
        results["valid"] = False
    else:
        context_window = model.get("context_window", 0)
        model_name = model.get("model_name", "")
        if not model_name:
            results["issues"].append("Model has no model_name")
            results["valid"] = False
        if context_window <= 0:
            results["warnings"].append(
                "Model context_window is missing or invalid"
            )
        else:
            results["model_ready"] = True

    # Prompt/content validation
    if not system_prompt or len(system_prompt.strip()) < 20:
        results["warnings"].append(
            "System prompt is very short; consider adding more instructions"
        )
    if not welcome_message:
        results["recommendations"].append(
            "Add a welcome_message to improve user onboarding"
        )

    # Tool validation
    for tool in tools:
        schema = tool.get("schema")
        if not schema:
            results["warnings"].append(
                f"Tool '{tool.get('name')}' has no JSON schema defined"
            )
        try:
            if isinstance(schema, str):
                json.loads(schema)
        except json.JSONDecodeError:
            results["issues"].append(
                f"Tool '{tool.get('name')}' has invalid JSON schema"
            )
            results["valid"] = False

    # Memory/history
    if memory_enabled and max_history <= 0:
        results["warnings"].append(
            "Memory is enabled but max_history is not set"
        )

    # Security
    if visibility == "public":
        results["warnings"].append(
            "Agent visibility is public; ensure tools do not expose sensitive data"
        )
        results["security_score"] = "medium"
    elif visibility == "restricted":
        results["security_score"] = "high"
    else:
        results["security_score"] = "high" if results["tool_count"] <= 5 else "medium"

    # Deployment readiness
    if results["provider_ready"] and results["model_ready"] and results["valid"]:
        results["recommendations"].append(
            "Agent is ready for deployment; consider testing in a private Discuss channel first"
        )
    else:
        results["recommendations"].append(
            "Resolve provider/model/configuration issues before deploying"
        )

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="analyze_ai_agent",
        description="Analyze an AI agent configuration for provider/model readiness, tools, and security",
        parameters={
            "type": "object",
            "properties": {
                "agent_data": {
                    "type": "object",
                    "description": "AI agent configuration dict"
                },
                "agent_id": {
                    "type": "integer",
                    "description": "Optional Odoo agent record ID"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Analysis with issues, warnings, recommendations, and readiness flags"
        },
        skill_id="skill_ai",
        category="analyzer",
        fn=analyze_ai_agent,
    ))


tools = [
    {
        "name": "analyze_ai_agent",
        "description": "Analyze an AI agent configuration for provider/model readiness, tools, and security",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_data": {"type": "object"},
                "agent_id": {"type": "integer"}
            }
        },
        "category": "analyzer",
        "fn": analyze_ai_agent,
    }
]

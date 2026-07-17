"""
AI Provider Config Validator Tool

Validates an ai.provider configuration: checks provider type,
credential presence, base URL formatting, timeout/retry settings,
and encryption/security exposure.
"""

import json
import re
from typing import Any, Dict, List, Optional

from tools.registry import ToolDefinition, ToolResult


SUPPORTED_PROVIDER_TYPES = {
    "openai", "anthropic", "azure_openai", "ollama", "groq", "custom"
}

URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


def validate_ai_provider_config(provider_data: Optional[dict] = None,
                                provider_id: Optional[int] = None,
                                strict: bool = True) -> dict:
    """
    Validate an AI provider configuration.

    Args:
        provider_data: Dict describing the ai.provider record
        provider_id: Optional Odoo record ID
        strict: If True, require API key for cloud providers

    Returns:
        Validation results with issues, warnings, and recommendations
    """
    results = {
        "provider_id": provider_id,
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
        "provider_type": None,
    }

    if not provider_data:
        results["valid"] = False
        results["issues"].append("No provider_data provided for validation")
        return results

    name = provider_data.get("name", "Unknown")
    provider_type = provider_data.get("provider_type")
    api_key = provider_data.get("api_key", "")
    base_url = provider_data.get("base_url", "")
    timeout = provider_data.get("timeout", 30)
    max_retries = provider_data.get("max_retries", 3)
    company_id = provider_data.get("company_id")

    results["provider_type"] = provider_type

    # Provider type
    if not provider_type:
        results["issues"].append("provider_type is required")
        results["valid"] = False
    elif provider_type not in SUPPORTED_PROVIDER_TYPES:
        results["warnings"].append(
            f"provider_type '{provider_type}' is not in the standard list: "
            f"{SUPPORTED_PROVIDER_TYPES}"
        )

    # Credentials
    cloud_providers = {"openai", "anthropic", "azure_openai", "groq"}
    if provider_type in cloud_providers:
        if strict and not api_key:
            results["issues"].append(
                f"Cloud provider '{provider_type}' requires an API key"
            )
            results["valid"] = False
        elif api_key and len(api_key) < 20:
            results["warnings"].append(
                "API key looks unusually short; verify it is correct"
            )

    if provider_type == "azure_openai":
        deployment = provider_data.get("deployment_name")
        api_version = provider_data.get("api_version")
        if not deployment:
            results["issues"].append(
                "Azure OpenAI requires deployment_name"
            )
            results["valid"] = False
        if not api_version:
            results["warnings"].append(
                "Azure OpenAI api_version not set; default may not match your deployment"
            )

    # Base URL
    if base_url:
        if not URL_RE.match(base_url):
            results["issues"].append(
                f"base_url '{base_url}' is not a valid HTTP(S) URL"
            )
            results["valid"] = False
        elif not base_url.startswith("https://"):
            results["warnings"].append(
                "base_url uses HTTP; HTTPS is recommended for production"
            )
    elif provider_type == "ollama":
        results["warnings"].append(
            "Ollama provider has no base_url; default http://localhost:11434 will be used"
        )

    # Timeout / retries
    if timeout is None or timeout <= 0:
        results["issues"].append("timeout must be a positive integer")
        results["valid"] = False
    elif timeout < 10:
        results["warnings"].append(
            "timeout is very short; some models may fail to respond"
        )

    if max_retries is None or max_retries < 0:
        results["issues"].append("max_retries must be >= 0")
        results["valid"] = False
    elif max_retries > 5:
        results["warnings"].append(
            "max_retries is high; this may delay failure feedback"
        )

    # Security / multi-company
    if company_id is None:
        results["recommendations"].append(
            "Set company_id to isolate provider credentials in multi-company environments"
        )

    if api_key and provider_data.get("api_key_encrypted") is False:
        results["issues"].append(
            "API key must be stored in an encrypted field"
        )
        results["valid"] = False

    if results["valid"] and not results["issues"]:
        results["recommendations"].append(
            f"Provider '{name}' is valid; test connectivity before assigning to agents"
        )

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_ai_provider_config",
        description="Validate AI provider configuration (credentials, URL, timeout, security)",
        parameters={
            "type": "object",
            "properties": {
                "provider_data": {
                    "type": "object",
                    "description": "AI provider configuration dict"
                },
                "provider_id": {
                    "type": "integer",
                    "description": "Optional Odoo provider record ID"
                },
                "strict": {
                    "type": "boolean",
                    "description": "Require API keys for cloud providers",
                    "default": True
                }
            }
        },
        returns={"type": "object", "description": "Validation results"},
        skill_id="skill_ai",
        category="validator",
        fn=validate_ai_provider_config,
    ))


tools = [
    {
        "name": "validate_ai_provider_config",
        "description": "Validate AI provider configuration (credentials, URL, timeout, security)",
        "parameters": {
            "type": "object",
            "properties": {
                "provider_data": {"type": "object"},
                "provider_id": {"type": "integer"},
                "strict": {"type": "boolean"}
            }
        },
        "category": "validator",
        "fn": validate_ai_provider_config,
    }
]

"""
Email Template Validator Tool

Validates email template definitions, QWeb syntax hints, and rendering
readiness for Odoo mail templates.
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_email_templates(
    template_data: Optional[dict] = None,
    templates: Optional[List[dict]] = None,
    strict: bool = False,
) -> dict:
    """
    Validate one or more email templates.

    Args:
        template_data: Dict with keys subject, body_html, email_from, email_to,
            partner_to, lang, report_template_ids.
        templates: List of template dicts for batch validation.
        strict: If True, treat warnings as issues.

    Returns:
        Validation results with valid flag, issues, warnings, and recommendations.
    """
    results = {
        "valid": True,
        "templates_checked": 0,
        "issues": [],
        "warnings": [],
        "recommendations": [],
    }

    items = templates or []
    if template_data:
        items.append(template_data)

    if not items:
        results["issues"].append("No template data provided.")
        results["valid"] = False
        return results

    results["templates_checked"] = len(items)

    for idx, template in enumerate(items):
        prefix = f"Template #{idx + 1}"
        if template.get("name"):
            prefix = f"'{template['name']}'"

        subject = template.get("subject", "")
        body = template.get("body_html", "")
        email_from = template.get("email_from", "")
        email_to = template.get("email_to", "")
        partner_to = template.get("partner_to", "")
        lang = template.get("lang", "")

        if not subject.strip():
            results["issues"].append(f"{prefix} is missing a subject.")
        if not body.strip():
            results["issues"].append(f"{prefix} is missing a body_html.")

        if not email_from and not template.get("user_signature"):
            results["warnings"].append(
                f"{prefix} has no email_from. Odoo will fall back to the company email."
            )

        if not email_to and not partner_to:
            results["warnings"].append(
                f"{prefix} has no email_to and no partner_to. No recipient will be resolved."
            )

        # Basic QWeb / placeholder sanity checks
        if body and "${" in body and "}" not in body:
            results["issues"].append(f"{prefix} body contains unclosed placeholder expression.")
        if body and "<t " in body and "</t>" not in body:
            results["warnings"].append(f"{prefix} body uses t- directives without closing tags.")

        if lang and not re.search(r"\$\{|object\.", lang):
            results["warnings"].append(
                f"{prefix} lang is static. Consider using ${{object.partner_id.lang}} for multi-language rendering."
            )

    if results["issues"]:
        results["valid"] = False

    if strict and results["warnings"]:
        results["valid"] = False

    if results["valid"]:
        results["recommendations"].append(
            "Templates are syntactically ready. Test render with a real record before deploying."
        )

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="validate_email_templates",
        description="Validate email templates for subject, recipients, body, and QWeb placeholders",
        parameters={
            "type": "object",
            "properties": {
                "template_data": {
                    "type": "object",
                    "description": "Single template dict to validate"
                },
                "templates": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of template dicts to validate"
                },
                "strict": {
                    "type": "boolean",
                    "description": "Treat warnings as validation failures",
                    "default": False
                }
            }
        },
        returns={
            "type": "object",
            "description": "Validation results with issues, warnings, and recommendations"
        },
        skill_id="skill_mail",
        category="validator",
        fn=validate_email_templates,
    ))


tools = [
    {
        "name": "validate_email_templates",
        "description": "Validate email templates for subject, recipients, body, and QWeb placeholders",
        "parameters": {
            "type": "object",
            "properties": {
                "template_data": {"type": "object"},
                "templates": {"type": "array", "items": {"type": "object"}},
                "strict": {"type": "boolean"}
            }
        },
        "category": "validator",
        "fn": validate_email_templates,
    }
]

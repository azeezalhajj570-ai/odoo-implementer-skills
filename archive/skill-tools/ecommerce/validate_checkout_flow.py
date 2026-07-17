"""
E-commerce Checkout Flow Validator Tool

Validates a checkout flow configuration or sale order and returns issues
related to cart contents, partner addresses, delivery carrier, and payment.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_checkout_flow(order: Optional[dict] = None,
                           providers: Optional[List[dict]] = None,
                           carriers: Optional[List[dict]] = None) -> dict:
    """
    Validate an e-commerce checkout flow.

    Args:
        order: Sale order dict with state, order_lines, partner_id,
               partner_invoice_id, partner_shipping_id, carrier_id, transaction_ids.
        providers: List of enabled payment provider dicts.
        carriers: List of available delivery carrier dicts.

    Returns:
        Validation results with issues and recommendations.
    """
    results = {
        "valid": True,
        "issues": [],
        "warnings": [],
        "recommendations": [],
        "steps_ready": {
            "cart": False,
            "billing_address": False,
            "shipping_address": False,
            "delivery": False,
            "payment": False,
        }
    }

    if not order:
        results["issues"].append("No sale order provided")
        results["valid"] = False
        return results

    lines = order.get("order_lines", []) or []
    if lines:
        results["steps_ready"]["cart"] = True
    else:
        results["issues"].append("Cart has no order lines")
        results["valid"] = False

    if order.get("partner_id"):
        results["steps_ready"]["billing_address"] = True
    else:
        results["issues"].append("Missing billing partner")
        results["valid"] = False

    if order.get("partner_shipping_id"):
        results["steps_ready"]["shipping_address"] = True
    else:
        results["warnings"].append("Missing explicit shipping partner; billing partner may be used")

    if order.get("carrier_id"):
        results["steps_ready"]["delivery"] = True
    else:
        results["warnings"].append("No delivery carrier selected")

    if order.get("transaction_ids"):
        results["steps_ready"]["payment"] = True
    else:
        results["warnings"].append("No payment transaction linked to the order")

    if providers:
        enabled_providers = [p for p in providers if p.get("state") == "enabled"]
        if not enabled_providers:
            results["issues"].append("No enabled payment providers available")
            results["valid"] = False
        else:
            results["recommendations"].append(
                f"Enabled payment providers: {', '.join(p.get('name') for p in enabled_providers)}"
            )
    else:
        results["warnings"].append("No payment provider configuration provided for validation")

    if carriers:
        available_carriers = [c for c in carriers if c.get("state") in ("enabled", True)]
        if not available_carriers:
            results["warnings"].append("No enabled delivery carriers available")
        if len(available_carriers) > 5:
            results["recommendations"].append(
                "Many delivery carriers are enabled; consider simplifying the customer choice"
            )
    else:
        results["warnings"].append("No delivery carrier configuration provided for validation")

    if order.get("state") not in ("draft", "sent"):
        results["issues"].append(
            f"Order is in state '{order.get('state')}' and cannot be checked out as a cart"
        )
        results["valid"] = False

    return results


def register(registry):
    """Register tools with the ToolRegistry."""
    from tools.registry import ToolDefinition

    registry.register(ToolDefinition(
        name="validate_checkout_flow",
        description="Validate an e-commerce checkout flow: cart, addresses, delivery, and payment",
        parameters={
            "type": "object",
            "properties": {
                "order": {
                    "type": "object",
                    "description": "Sale order dictionary representing the cart"
                },
                "providers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of payment provider dictionaries"
                },
                "carriers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of delivery carrier dictionaries"
                }
            }
        },
        returns={
            "type": "object",
            "description": "Validation results with readiness flags, issues, and recommendations"
        },
        skill_id="skill_ecommerce",
        category="validator",
        fn=validate_checkout_flow,
    ))


tools = [
    {
        "name": "validate_checkout_flow",
        "description": "Validate an e-commerce checkout flow: cart, addresses, delivery, and payment",
        "parameters": {
            "type": "object",
            "properties": {
                "order": {"type": "object"},
                "providers": {"type": "array", "items": {"type": "object"}},
                "carriers": {"type": "array", "items": {"type": "object"}}
            }
        },
        "category": "validator",
        "fn": validate_checkout_flow,
    }
]

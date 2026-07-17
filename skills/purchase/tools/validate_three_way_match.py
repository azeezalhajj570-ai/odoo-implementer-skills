"""
Purchase Three-Way Match Validator Tool

Validates purchase/receipt/bill alignment for quantities and prices.
"""

from typing import Any, Dict, List, Optional
from tools.registry import ToolDefinition


def validate_three_way_match(po_lines: Optional[List[dict]] = None,
                              receipt_lines: Optional[List[dict]] = None,
                              bill_lines: Optional[List[dict]] = None,
                              price_tolerance: float = 0.01,
                              qty_tolerance: float = 0.01) -> dict:
    """
    Validate three-way matching between PO, receipt, and vendor bill.

    Args:
        po_lines: PO lines with product_id, product_qty, price_unit
        receipt_lines: Receipt lines with product_id, quantity_done
        bill_lines: Bill lines with product_id, quantity, price_unit
        price_tolerance: Allowed relative price difference
        qty_tolerance: Allowed relative quantity difference

    Returns:
        Validation results with exceptions and recommendations
    """
    results = {
        "valid": True,
        "exceptions": [],
        "recommendations": [],
    }

    if not po_lines:
        results["exceptions"].append("No purchase order lines provided")
        results["valid"] = False
        return results

    po_map = {line.get("product_id"): line for line in po_lines}
    receipt_map = {line.get("product_id"): line for line in (receipt_lines or [])}
    bill_map = {line.get("product_id"): line for line in (bill_lines or [])}

    for product_id, po_line in po_map.items():
        po_qty = po_line.get("product_qty", 0)
        po_price = po_line.get("price_unit", 0)
        rec_line = receipt_map.get(product_id)
        bill_line = bill_map.get(product_id)

        if not rec_line:
            results["exceptions"].append(
                f"Product {product_id}: ordered but not received"
            )
            results["valid"] = False
        else:
            rec_qty = rec_line.get("quantity_done", 0)
            if po_qty and abs(rec_qty - po_qty) / po_qty > qty_tolerance:
                results["exceptions"].append(
                    f"Product {product_id}: receipt qty {rec_qty} differs from PO qty {po_qty}"
                )
                results["valid"] = False

        if not bill_line:
            results["exceptions"].append(
                f"Product {product_id}: ordered but not billed"
            )
            results["valid"] = False
        else:
            bill_qty = bill_line.get("quantity", 0)
            bill_price = bill_line.get("price_unit", 0)
            if rec_line and rec_line.get("quantity_done", 0):
                rec_qty = rec_line.get("quantity_done", 0)
                if abs(bill_qty - rec_qty) / rec_qty > qty_tolerance:
                    results["exceptions"].append(
                        f"Product {product_id}: billed qty {bill_qty} differs from receipt qty {rec_qty}"
                    )
                    results["valid"] = False
            if po_price and abs(bill_price - po_price) / po_price > price_tolerance:
                results["exceptions"].append(
                    f"Product {product_id}: billed price {bill_price} differs from PO price {po_price}"
                )
                results["valid"] = False

    if not results["valid"]:
        results["recommendations"].append("Review exceptions before validating the vendor bill")

    return results


def register(registry):
    registry.register(ToolDefinition(
        name="validate_three_way_match",
        description="Validate PO/receipt/bill three-way matching",
        parameters={
            "type": "object",
            "properties": {
                "po_lines": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "PO lines"
                },
                "receipt_lines": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Receipt lines"
                },
                "bill_lines": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Vendor bill lines"
                },
                "price_tolerance": {
                    "type": "number",
                    "description": "Relative price tolerance",
                    "default": 0.01
                },
                "qty_tolerance": {
                    "type": "number",
                    "description": "Relative quantity tolerance",
                    "default": 0.01
                }
            }
        },
        returns={"type": "object", "description": "Three-way match validation results"},
        skill_id="skill_purchase",
        category="validator",
        fn=validate_three_way_match,
    ))


tools = [
    {
        "name": "validate_three_way_match",
        "description": "Validate PO/receipt/bill three-way matching",
        "parameters": {
            "type": "object",
            "properties": {
                "po_lines": {"type": "array", "items": {"type": "object"}},
                "receipt_lines": {"type": "array", "items": {"type": "object"}},
                "bill_lines": {"type": "array", "items": {"type": "object"}},
                "price_tolerance": {"type": "number"},
                "qty_tolerance": {"type": "number"}
            }
        },
        "category": "validator",
        "fn": validate_three_way_match,
    }
]

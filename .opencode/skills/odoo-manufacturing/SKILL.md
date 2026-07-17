---
name: odoo-manufacturing
description: Use when the user asks about Odoo Manufacturing Expert topics such as Bill of Materials Design, Routing & Operations, Work Center Management in Odoo 19. Loads knowledge from skills/manufacturing/.
---

# Skill: odoo-manufacturing

Odoo Manufacturing Expert — Expert-level knowledge of Odoo 19 Manufacturing (MRP): bills of materials, routings, operations, work centers, manufacturing orders, work orders, shop floor execution, subcontracting, by-products, MRP planning, procurement integration, and quality checkpoints. Use when the user asks about Bill of Materials Design, Routing & Operations, Work Center Management, Manufacturing Orders & Scheduling, Work Orders & Shop Floor in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/manufacturing/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/manufacturing/skill.json` — metadata, modules, dependencies
   - `skills/manufacturing/capability.json` — detailed capability definitions
   - `skills/manufacturing/knowledge.json` — key models, files, crons, security groups
   - `skills/manufacturing/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Bill of Materials Design** (`cap_bom_design`): Design multi-level BOMs with components, quantities, units of measure, operations, by-products, and variants. Distinguish normal, phantom, and subcontracting BOM types.
- **Routing & Operations** (`cap_routing_operations`): Define routings, operations, sequences, default work centers, time tracking (setup/operation), and attach routings to BOMs for capacity planning.
- **Work Center Management** (`cap_workcenter_management`): Configure work centers, alternative work centers, capacity (hours/pieces), time efficiency, OEE targets, costs, and working calendars.
- **Manufacturing Orders & Scheduling** (`cap_manufacturing_orders`): Create, plan, confirm, and close manufacturing orders. Understand MRP-generated vs manual MOs, reservation, backorders, and lead-time computation.
- **Work Orders & Shop Floor** (`cap_workorders_shopfloor`): Execute work orders, operator time tracking, shop floor tablet view, OEE calculations, production logging, and step-by-step operation control.
- **Subcontracting** (`cap_subcontracting`): Manage subcontracted manufacturing: send raw materials to vendor, receive finished goods, track subcontractor stock, and generate vendor bills.
- **By-Products & Scrap** (`cap_byproducts_scrap`): Configure by-product lines on BOMs, report produced by-products, and account for scrap during operations with stock scrap reasons.
- **MRP Planning & Procurement** (`cap_mrp_planning`): Run MRP, read procurement exceptions, configure orderpoints/reordering rules, safety stock, make-to-order, and master production schedule integration.
- **Quality Integration** (`cap_quality_integration`): Link quality checks and control points to operations, work orders, and finished goods using quality_mrp.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- MRP computation can be resource-intensive on large BOM trees; run scheduler during off-peak hours
- Shop floor tablet and advanced OEE require the mrp_workorder Enterprise module
- Subcontracting requires the mrp_subcontracting module and vendor configured as subcontractor

## Context

- **Domain:** Operations
- **Subdomain:** Manufacturing
- **Skill ID:** skill_manufacturing
- **Knowledge package:** `skills/manufacturing/`

- **Required modules:** mrp
- **Optional modules:** mrp_workorder, mrp_subcontracting, mrp_plm, quality_mrp

- **Depends on skills:** skill_base, skill_inventory
- **Relevant modules:** mrp, stock, product, uom

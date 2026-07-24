---
name: odoo-inventory
description: Use when the user asks about Odoo Inventory Expert topics such as Product & Product Variants, Warehouses & Locations, Stock Moves & Pickings in Odoo 19. Loads knowledge from skills/inventory/.
---

# Skill: odoo-inventory

Odoo Inventory Expert — Expert-level knowledge of Odoo Inventory including products, warehouses, locations, stock moves, picking types, routes, reordering rules, lots/serial tracking, valuation, MTS/MTO, and barcode operations. Use when the user asks about Product & Product Variants, Warehouses & Locations, Stock Moves & Pickings, Routes & Rules, Reordering Rules in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/inventory/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/inventory/skill.json` — metadata, modules, dependencies
   - `skills/inventory/capability.json` — detailed capability definitions
   - `skills/inventory/knowledge.json` — key models, files, crons, security groups
   - `skills/inventory/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Product & Product Variants** (`cap_products`): Configure product.template, product.product, product categories, UoM, routes, tracking modes (none, lot, serial), and inventory valuation categories.
- **Warehouses & Locations** (`cap_warehouses`): Manage stock.warehouse, stock.location (internal, supplier, customer, inventory loss, transit), location types, and hierarchies.
- **Stock Moves & Pickings** (`cap_stock_moves`): Create and manage stock.move, stock.picking, stock.picking.type, move lines, states, and reservation logic.
- **Routes & Rules** (`cap_routes`): Configure stock.route, stock.rule, procurement groups, push/pull rules, and MTS/MTO rules across warehouses.
- **Reordering Rules** (`cap_reordering`): Manage stock.warehouse.orderpoint (reordering rules), min/max quantities, order quantities, and triggering RFQs/sales orders.
- **Lots & Serial Tracking** (`cap_lots_serial`): Enable lot/serial tracking, manage stock.lot, expiration dates, removal strategies (FEFO, FIFO, LIFO), and traceability reports.
- **Inventory Valuation** (`cap_valuation`): Configure stock valuation categories, cost methods, stock_account, automatic inventory valuation, and landed costs (Enterprise).
- **MTS/MTO & Procurement** (`cap_mts_mto`): Configure Make-to-Stock vs Make-to-Order behavior, procurement rules, supply methods, and cross-dock/transit flows.
- **Barcode Operations** (`cap_barcode`): Use Enterprise stock_barcode for mobile picking, receiving, transfers, inventory adjustments, and barcode scanning workflows.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Barcode operations require Enterprise stock_barcode
- Landed costs and advanced valuation are Enterprise features
- Manufacturing integration requires the mrp module
- Lot/serial tracking cannot be changed on products with existing stock moves

## Context

- **Domain:** Operations
- **Subdomain:** Inventory
- **Skill ID:** skill_inventory
- **Knowledge package:** `skills/inventory/`

- **Required modules:** stock
- **Optional modules:** stock_account, purchase_stock, sale_stock, stock_barcode, stock_landed_costs

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** stock, product, uom, mail, purchase, sale

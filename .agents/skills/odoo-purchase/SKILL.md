# Skill: odoo-purchase

Odoo Purchase Expert — Expert-level knowledge of Odoo 19 Purchase: RFQs, purchase orders, vendor management, supplier pricelists, procurement rules, dropshipping, landed costs, vendor bills, three-way matching, and purchase agreements. Use when the user asks about RFQ & Purchase Order Management, Vendor Management, Purchase Pricelists & Discounts, Procurement & Replenishment, Dropshipping in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/purchase/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/purchase/skill.json` — metadata, modules, dependencies
   - `skills/purchase/capability.json` — detailed capability definitions
   - `skills/purchase/knowledge.json` — key models, files, crons, security groups
   - `skills/purchase/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **RFQ & Purchase Order Management** (`cap_rfq_purchase_orders`): Create and manage RFQs and POs, vendor communication, confirmation, amendments, and receipt/billing tracking.
- **Vendor Management** (`cap_vendor_management`): Configure vendors, supplier info, vendor evaluation, multiple addresses, and payment terms.
- **Purchase Pricelists & Discounts** (`cap_purchase_pricelists`): Set up product.supplierinfo records, quantity breaks, min qty, multiple currencies, and discount fields.
- **Procurement & Replenishment** (`cap_procurement_replenishment`): Use reordering rules, make-to-order, buy routes, and procurement groups to automate purchase proposals.
- **Dropshipping** (`cap_dropshipping`): Configure dropship route and rules so vendors ship directly to customers without stocking goods.
- **Landed Costs** (`cap_landed_costs`): Allocate freight, insurance, and duty costs to received stock using stock.landed.cost.
- **Vendor Bills & Three-Way Matching** (`cap_vendor_bills_matching`): Create vendor bills from PO/receipts, match quantities and prices, and handle price/quantity exceptions.
- **Purchase Agreements & Blanket Orders** (`cap_purchase_agreements`): Use purchase.requisition to create blanket orders, call for tenders, and compare vendor quotations.
- **Purchase Approval Workflows** (`cap_approval_workflows`): Configure multi-level approvals, budget limits, and team-based approval rules.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Three-way matching requires purchase, stock, and accounting modules installed
- Landed costs are applied on receipt validation and may require manual splits
- Purchase blanket orders do not automatically release against incoming demand unless configured

## Context

- **Domain:** Operations
- **Subdomain:** Purchase
- **Skill ID:** skill_purchase
- **Knowledge package:** `skills/purchase/`

- **Required modules:** purchase
- **Optional modules:** purchase_requisition, purchase_stock, stock_dropshipping, stock_landed_costs

- **Depends on skills:** skill_base, skill_inventory
- **Relevant modules:** purchase, purchase_stock, stock, product, account

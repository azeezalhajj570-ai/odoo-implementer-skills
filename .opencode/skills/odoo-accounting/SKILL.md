---
name: odoo-accounting
description: Use when the user asks about Odoo Accounting Expert topics such as Chart of Accounts, Journal Configuration, Invoice Management in Odoo 19. Loads knowledge from skills/accounting/.
---

# Skill: odoo-accounting

Odoo Accounting Expert — Expert-level knowledge of Odoo Accounting including chart of accounts, journals, invoices, payments, taxes, bank reconciliation, fiscal positions, assets, and financial reports (P&L, balance sheet, cash flow). Use when the user asks about Chart of Accounts, Journal Configuration, Invoice Management, Payments & Bank, Tax Configuration in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/accounting/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/accounting/skill.json` — metadata, modules, dependencies
   - `skills/accounting/capability.json` — detailed capability definitions
   - `skills/accounting/knowledge.json` — key models, files, crons, security groups
   - `skills/accounting/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Chart of Accounts** (`cap_chart_of_accounts`): Configure account.chart.template, account.account, account.group. Manage account types, codes, reconciliation flags, and fiscal localization packages.
- **Journal Configuration** (`cap_journals`): Configure account.journal with types (sale, purchase, cash, bank, general), sequences, default accounts, bank accounts, and payment methods.
- **Invoice Management** (`cap_invoices`): Create and manage customer invoices, vendor bills, credit notes, refunds, and invoice lines. Handle invoice states (draft, posted, cancel), payment references, and portal sending.
- **Payments & Bank** (`cap_payments`): Process account.payment records, payment methods, reconciliation, outstanding receipts/payments accounts, and batch payments.
- **Tax Configuration** (`cap_taxes`): Configure account.tax, tax groups, tax grids, report lines, and fiscal positions. Handle inclusive/exclusive taxes, tax clouds, and multi-company tax setups.
- **Bank Reconciliation** (`cap_reconciliation`): Use account.bank.statement, account.bank.statement.line, and account.reconcile.model to match bank transactions with open invoices and journal entries.
- **Fiscal Positions** (`cap_fiscal_positions`): Manage account.fiscal.position for tax and account mapping across countries, intra-community, and B2B/B2C rules.
- **Asset Management** (`cap_assets`): Configure account.asset, depreciation boards, asset categories, disposal, and depreciation journals using Enterprise account_asset.
- **Financial Reports** (`cap_reports`): Generate and configure P&L, balance sheet, cash flow, general ledger, trial balance, and aged receivables/payables using Enterprise account_reports.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Some advanced reports and bank statement import require Enterprise modules
- Localization packages are required for country-specific charts of accounts and taxes
- Accountant-level changes should be reviewed by a finance professional
- Asset depreciation and fiscal year closing require careful date planning

## Context

- **Domain:** Finance
- **Subdomain:** Accounting
- **Skill ID:** skill_accounting
- **Knowledge package:** `skills/accounting/`

- **Required modules:** account
- **Optional modules:** account_accountant, account_bank_statement_import, account_asset, account_reports

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** account, base_setup, product, analytic, portal

# Skill: odoo-skills-router

Route Odoo questions to the right domain-specific skill. Use when the user asks about Odoo in general, wants to know which skill applies, or mentions a domain without a clear workflow skill invocation.

## Routing table

| If the user asks about... | Use skill |
|---------------------------|-----------|
| Accounting, invoices, payments, taxes, fiscal years | `odoo-accounting` |
| Odoo AI module, agent integration, AI skills | `odoo-ai` |
| ORM, security, views, mail, automation, controllers, reports | `odoo-base` |
| CRM, pipelines, leads, lead scoring, mining, enrichment | `odoo-crm` |
| Module development, models, OWL, controllers, testing | `odoo-development` |
| eCommerce, website shop, checkout, products online | `odoo-ecommerce` |
| HR, employees, recruitment, payroll, attendance | `odoo-hr` |
| Inventory, warehouses, stock moves, replenishment | `odoo-inventory` |
| Mail, notifications, email templates, messaging | `odoo-mail` |
| Manufacturing, BOMs, work orders, MRP | `odoo-manufacturing` |
| Marketing automation, campaigns, lead nurturing | `odoo-marketing` |
| Migration between Odoo versions, upgrade scripts | `odoo-migration` |
| Platform recovery, salvage, broken instance repair | `odoo-platform-recovery` |
| Project management, tasks, timesheets, planning | `odoo-project` |
| Purchase orders, vendors, RFQs, procurement | `odoo-purchase` |
| Security, ACLs, record rules, groups, GDPR | `odoo-security` |
| Social marketing, social media posts, campaigns | `odoo-social-marketing` |
| Technical due diligence, code review, architecture assessment | `odoo-technical-due-diligence` |
| Website builder, pages, themes, SEO, portals | `odoo-website` |

## Process

1. Identify the domain from the user's message.
2. If the domain is clear, load the matching skill and continue with its process.
3. If the domain is unclear or spans multiple domains, ask the user which one to focus on first.
4. If the user explicitly asks for a comparison across domains, consult the relevant skills in order and synthesize the answer.

## Cross-cutting concerns

For questions that touch multiple domains (e.g., "How do I set up sales, inventory, and accounting for a trading company?"), route through each relevant skill and present an integrated answer. Start with the most foundational domain (`odoo-base` for ORM/security) then cover the business domains in dependency order.

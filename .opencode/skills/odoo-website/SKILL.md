---
name: odoo-website
description: Use when the user asks about Odoo Website Expert topics such as Website Builder & Pages, Themes & Snippets, E-Commerce Product Pages in Odoo 19. Loads knowledge from skills/website/.
---

# Skill: odoo-website

Odoo Website Expert — Expert-level knowledge of Odoo 19 Website: website builder, pages, themes, snippets, e-commerce product pages, cart, checkout, blog, SEO, portal, and OWL frontend components. Use when the user asks about Website Builder & Pages, Themes & Snippets, E-Commerce Product Pages, Cart & Checkout, Blog & Content in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/website/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/website/skill.json` — metadata, modules, dependencies
   - `skills/website/capability.json` — detailed capability definitions
   - `skills/website/knowledge.json` — key models, files, crons, security groups
   - `skills/website/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Website Builder & Pages** (`cap_website_builder_pages`): Create and manage website pages, menus, redirects, and the website builder using drag-and-drop snippets.
- **Themes & Snippets** (`cap_themes_snippets`): Install and customize themes, configure color/fonts, and extend or create website snippets.
- **E-Commerce Product Pages** (`cap_ecommerce_products`): Publish products on the website, configure product variants, filters, categories, and alternative products.
- **Cart & Checkout** (`cap_cart_checkout`): Configure shopping cart, payment providers, delivery methods, checkout flow, and abandoned carts.
- **Blog & Content** (`cap_blog_content`): Create blogs and posts, manage categories, authors, publishing schedules, and content blocks.
- **SEO & Metadata** (`cap_seo_metadata`): Optimize page titles, meta descriptions, URL slugs, sitemap, structured data, and social sharing.
- **Portal & Customer Account** (`cap_portal_account`): Configure portal access, customer account pages, orders, invoices, projects, and profile management.
- **OWL Frontend Components** (`cap_owl_frontend`): Build and customize OWL-based frontend interactions, public widgets, and website editor integrations.
- **Website Forms & Lead Capture** (`cap_forms_leads`): Create contact forms, configure CRM lead creation, and integrate marketing automation with website pages.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Full e-commerce checkout requires payment provider and delivery modules
- Custom OWL components may need asset bundles and frontend compatibility testing
- Multi-website configurations require careful domain and page routing setup

## Context

- **Domain:** Website
- **Subdomain:** Website
- **Skill ID:** skill_website
- **Knowledge package:** `skills/website/`

- **Required modules:** website
- **Optional modules:** website_sale, website_blog, website_payment, portal

- **Depends on skills:** skill_base, skill_crm
- **Relevant modules:** website, web, mail, portal

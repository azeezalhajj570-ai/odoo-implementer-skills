---
name: odoo-ecommerce
description: Use when the user asks about Odoo eCommerce Expert topics such as Product Catalog Management, Product Variants & Combinations, Pricelists & Price Rules in Odoo 19. Loads knowledge from skills/ecommerce/.
---

# Skill: odoo-ecommerce

Odoo eCommerce Expert — Expert-level knowledge of Odoo eCommerce including product catalog and variants, public categories, pricelists and price rules, cart and checkout flow, payment providers, delivery carriers, wishlists and product comparisons, digital products, abandoned cart recovery, and SEO-optimized product pages. Use when the user asks about Product Catalog Management, Product Variants & Combinations, Pricelists & Price Rules, Cart & Checkout Flow, Payment Providers in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/ecommerce/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/ecommerce/skill.json` — metadata, modules, dependencies
   - `skills/ecommerce/capability.json` — detailed capability definitions
   - `skills/ecommerce/knowledge.json` — key models, files, crons, security groups
   - `skills/ecommerce/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Product Catalog Management** (`cap_product_catalog`): Publish products, configure public categories, images, descriptions, SEO metadata, and product visibility for website shoppers.
- **Product Variants & Combinations** (`cap_product_variants`): Configure product templates with attribute lines and values, manage variant extra prices, availability, and product configurator on the shop.
- **Pricelists & Price Rules** (`cap_pricelists`): Configure advanced pricelists, price rules, currency-based pricing, and website-specific pricelist assignment.
- **Cart & Checkout Flow** (`cap_cart_checkout`): Manage sale orders created as e-commerce carts, address collection, express checkout, cart recovery, and guest checkout behavior.
- **Payment Providers** (`cap_payment_providers`): Configure payment providers, payment methods, tokens, capture modes, and transaction flow integration with sale orders.
- **Delivery Methods & Shipping** (`cap_delivery_methods`): Set up delivery carriers, shipping cost rules, carrier-specific connectors, and delivery line injection during checkout.
- **Wishlists & Product Comparisons** (`cap_wishlist_comparison`): Enable customer wishlists, comparison lists, and customer-specific product interactions tied to website visitors and portal users.
- **Digital Products** (`cap_digital_products`): Configure downloadable products, attachments, and post-payment digital delivery through customer portal downloads.
- **Product SEO & Shop Optimization** (`cap_seo_products`): Optimize product pages for search engines, manage sitemap entries, structured data, meta tags, and URL slugs for the shop.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Payment providers require valid acquiring credentials and may be subject to region availability
- Delivery carrier live rates require carrier-specific API integration or third-party modules
- Wishlist and comparison features require portal/visitor tracking and are limited to authenticated or cookied users
- Abandoned cart recovery only applies to carts that have a known email or partner
- Digital product downloads depend on portal attachment access and product type configuration

## Context

- **Domain:** Website
- **Subdomain:** eCommerce
- **Skill ID:** skill_ecommerce
- **Knowledge package:** `skills/ecommerce/`

- **Required modules:** website_sale, sale, product, payment
- **Optional modules:** delivery, website, portal

- **Depends on skills:** skill_base, skill_website, skill_crm
- **Relevant modules:** website_sale, sale, product, payment, delivery, website, portal

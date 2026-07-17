# Skill: odoo-base

Odoo Platform Foundation — Core Odoo platform knowledge including ORM, security, views, mail framework, automation, and system architecture. Required by all domain skills. Use when the user asks about Odoo ORM, Odoo Security, XML Views, Automation Framework, Mail Framework in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/base/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/base/skill.json` — metadata, modules, dependencies
   - `skills/base/capability.json` — detailed capability definitions
   - `skills/base/knowledge.json` — key models, files, crons, security groups
   - `skills/base/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Odoo ORM** (`cap_orm`): Model definition, fields, inheritance, computed fields, constraints, search, read, write, create, unlink
- **Odoo Security** (`cap_security`): Access control lists, record rules, security groups, implied groups, field-level security
- **XML Views** (`cap_views`): Form, tree, kanban, search, graph, pivot, calendar, gantt, activity views with inheritance and xpath
- **Automation Framework** (`cap_automation`): Server actions, automated actions, cron jobs, scheduled actions
- **Mail Framework** (`cap_mail`): mail.thread, mail.activity.mixin, notifications, templates, email routing, bounce handling
- **HTTP Controllers** (`cap_controllers`): Route definitions, authentication, request handling, response formats
- **QWeb Reports** (`cap_reports`): PDF/HTML report generation, paper formats, barcodes, custom reports
- **Internationalization** (`cap_i18n`): Translations, translatable fields, language support, i18n tools
- **Testing** (`cap_testing`): TransactionCase, HttpCase, test tags, mock patterns, performance testing

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Does not cover domain-specific business logic
- Generic ORM knowledge; domain-specific models require domain skills

## Context

- **Domain:** Platform
- **Subdomain:** Core
- **Skill ID:** skill_base
- **Knowledge package:** `skills/base/`

- **Required modules:** base, web, mail

- **Relevant modules:** base, web, mail

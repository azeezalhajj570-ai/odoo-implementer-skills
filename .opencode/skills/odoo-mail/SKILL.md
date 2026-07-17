---
name: odoo-mail
description: Use when the user asks about Odoo Mail & Communication Framework topics such as mail.thread, Mail Activities, Email Templates in Odoo 19. Loads knowledge from skills/mail/.
---

# Skill: odoo-mail

Odoo Mail & Communication Framework — Expert knowledge of Odoo's mail, discuss, and notification framework including mail.thread, mail.activity.mixin, mail templates, email routing, bounce handling, notifications, and chatter. Use when the user asks about mail.thread, Mail Activities, Email Templates, Notifications, Bounce Handling in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/mail/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/mail/skill.json` — metadata, modules, dependencies
   - `skills/mail/capability.json` — detailed capability definitions
   - `skills/mail/knowledge.json` — key models, files, crons, security groups
   - `skills/mail/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **mail.thread** (`cap_mail_thread`): Message tracking, notifications, followers, subtypes, routing, bounce handling. Key methods: message_post, message_subscribe, message_route_process, _routing_handle_bounce.
- **Mail Activities** (`cap_activities`): mail.activity.mixin, activity plans, activity types, scheduling, calendar integration, deadline management.
- **Email Templates** (`cap_email_templates`): QWeb-based email templates, template inheritance, dynamic placeholders, AI prompt integration, render engine.
- **Notifications** (`cap_notifications`): In-app notifications, email notifications, SMS notifications, push notifications, digest emails.
- **Bounce Handling** (`cap_bounce_handling`): Inbound email routing, bounce detection, auto-blacklist after 5 bounces/3 months, failure type classification (mail_bounce, mail_spam, mail_smtp, etc.).

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- None documented.

## Context

- **Domain:** Platform
- **Subdomain:** Mail & Communication
- **Skill ID:** skill_mail
- **Knowledge package:** `skills/mail/`

- **Required modules:** mail

- **Depends on skills:** skill_base
- **Relevant modules:** mail, bus

---
name: odoo-executive-assistant
description: Use when the user asks about creating or configuring an Odoo Executive Assistant AI agent for calendar management, email, discuss communication, activity management, and AI agent setup in Odoo 19. Loads knowledge from skills/executive_assistant/.
---

# Skill: odoo-executive-assistant

Odoo Executive Assistant Expert — create and configure Odoo AI agents for calendar management (create/update/cancel/list events, find slots), email (read inbox, send, templates, search partners), discuss communication (channel messages), and activity management (create/complete activities). Covers ai.agent, ai.topic, ir.actions.server tools, ai.composer, and ai.prompt.button setup.

## Domain anchors

- Reference exact model and field names when implementing tools.
- Follow the naming convention: `AI: <Verb> <Noun>` for server action tools.
- Always set `use_in_ai=True` on server actions before linking to topics.
- Use `partner_ids` (not `message_partner_ids`) when searching mail.message.
- Use XML-RPC for many2many writes on tool_ids (MCP limitation).

## Process

1. **Clarify the task**
   Determine if the user needs agent creation, tool development, topic configuration, composer/prompt setup, or troubleshooting. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**
   Read the relevant files for this skill:
   - `skills/executive_assistant/skill.json` — metadata, modules, dependencies
   - `skills/executive_assistant/capability.json` — detailed capability definitions
   - `skills/executive_assistant/knowledge.json` — key models, fields, error patterns
   - `skills/executive_assistant/prompt.md` — the system prompt for this domain

3. **Select the right capability**
   Match the user's request to one of the domain capabilities:

   - **Executive Assistant Agent Setup** (`cap_ea_agent_setup`): Create and configure ai.agent with system prompt, model, style, and topic linking.
   - **Tool Creation** (`cap_ea_tool_creation`): Build server actions as AI tools for calendar, email, discuss, activity operations.
   - **Topic Configuration** (`cap_ea_topic_config`): Create ai.topic with instructions and link tools (use_in_ai=True required first).
   - **Composer & Prompt Buttons** (`cap_ea_composer_prompts`): Create ai.composer for systray/chatter/email and add ai.prompt.button records.
   - **Test Data** (`cap_ea_test_data`): Create sample contacts, events, emails, and channels for agent testing.

4. **Produce output**
   Return one of: configuration steps, Python code for server actions, XML-RPC snippets, or a concise explanation. Include required modules and any limitations.

5. **Verify**
   Cross-check against the known error patterns (use_in_ai=False, wrong field name, MCP many2many limitation).

## Limitations

- MCP write pipeline does not persist many2many commands — use XML-RPC for tool_ids linking
- `ai.agent` has no `description` field — use `subtitle` instead
- `mail.message` uses `partner_ids` (not `message_partner_ids`) for recipient filtering
- Server actions must use safe_eval-compatible Python (no imports, no complex syntax)
- `mail.activity.state` is computed (not stored) — cannot filter by it in domains
- `tool_ids` on ai.topic has domain `[['use_in_ai', '=', True]]` and group `base.group_system`

## Context

- **Domain:** Productivity
- **Subdomain:** AI Assistant
- **Skill ID:** skill_executive_assistant
- **Knowledge package:** `skills/executive_assistant/`

- **Required modules:** ai_app, mail, calendar
- **Optional modules:** discuss, social_marketing

- **Depends on skills:** skill_base, skill_mail, skill_ai
- **Relevant modules:** ai_app, mail, calendar, discuss

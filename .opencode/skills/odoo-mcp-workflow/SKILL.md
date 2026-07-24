---
name: odoo-mcp-workflow
description: Use when the user asks about Odoo AI Agent development workflow, MCP tool usage patterns, Odoo AI internals, and conventions for building agents, topics, tools, and composer integrations in Odoo 19. Loads knowledge from skills/mcp_workflow/.
---

# Skill: odoo-mcp-workflow

Odoo MCP Workflow Expert — guides how to use the Odoo MCP server tools, create AI agents following Odoo's internal architecture, apply consistent naming/structure patterns, and follow the user's established conventions and rules.

## Domain anchors

- MCP tools are the primary interface; XML-RPC is the fallback when MCP cannot handle the operation.
- Always match existing Odoo patterns (naming, structure, architecture) — never invent new conventions.
- Document every step, record every decision, and save session context.
- Prefer Odoo 19 syntax and patterns exclusively.
- Safety: never expose secrets, never commit without explicit request, never execute destructive operations unless explicitly asked.

---

## Part 1: Using the Odoo MCP

### Primary MCP Tools

| Tool | When to Use |
|------|-------------|
| `odoo_search_records` | Search/read records with domain filters |
| `odoo_read_record` | Read a single record by ID with specific fields |
| `odoo_get_model_fields` | Inspect field definitions on any model |
| `odoo_aggregate_records` | Group/sum/count across records |
| `odoo_list_models` | Find available models by name pattern |
| `odoo_validate_write` | Preview a create/write before executing |
| `odoo_execute_approved_write` | Execute a previously validated create/write |
| `odoo_chatter_post` | Post a message on a mail.thread record |
| `odoo_execute_method` | Run reviewed model methods (blocked for side-effects by default) |
| `odoo_health_check` | Verify Odoo connection status |

### MCP Limitations

| Limitation | Workaround |
|------------|------------|
| `execute_approved_write` does NOT persist many2many commands | Use XML-RPC: `models.execute_kw(db, uid, password, 'model', 'write', [[id], {'field': [(6,0,[ids])]}])` |
| `execute_method` blocks ALL side-effect methods | Use MCP writes for CRUD, XML-RPC for custom methods |
| Writes return True but many2many fields stay empty | Check domain filters on the field (e.g. `use_in_ai=True` requirement on tool_ids) |

### XML-RPC Connection Pattern

```python
import xmlrpc.client, ssl
url, db, username, password = "https://example.com", "db", "admin", "pass"
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", context=ssl._create_unverified_context())
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", context=ssl._create_unverified_context())
# Then: models.execute_kw(db, uid, password, 'model', 'method', [args], {kwargs})
```

---

## Part 2: Odoo AI Agent Architecture

### The Full Stack

```
User Interface (Discuss / Systray / Chatter / Email Composer)
       ↓
ai.composer — links agent to a specific UI surface
       ↓
ai.agent — the AI model (LLM, system prompt, response style)
       ↓
ai.topic — instructions + linked tools (many2many)
       ↓
ir.actions.server — tools as Python code on ai.agent model
```

### How It Works

1. User interacts through a UI surface (systray AI button, chatter button, email composer)
2. The `ai.composer` determines which agent handles the request
3. The agent receives the user's message + system prompt + topic instructions
4. The agent's LLM decides which tools (server actions) to invoke based on topic instructions
5. Each tool runs Python code via `safe_eval` and returns results via `ai['result']`
6. The agent processes results and responds to the user

### Agent Fields

- `name`: Display name
- `subtitle`: Description (there is NO `description` field)
- `system_prompt`: Instructions for the LLM — follow Ask AI pattern
- `llm_model`: Model selection (openrouter/free, gemini-2.5-flash, etc.)
- `response_style`: analytical | balanced | creative
- `topic_ids`: many2many to ai.topic
- `partner_id`: res.partner for the agent
- `source_id`: utm.source for tracking
- `restrict_to_sources`: bool — limit responses to attached sources

### Server Action Tool Pattern

```python
# Each tool is an ir.actions.server record:
{
    'name': 'AI: <Verb> <Noun>',      # Naming convention
    'model_id': 351,                    # ai.agent model ID
    'state': 'code',
    'usage': 'ir_actions_server',
    'binding_type': 'action',
    'use_in_ai': True,                  # REQUIRED for topic linking
    'code': '''
try:
    # Use env, ai, record from safe_eval context
    result = env['model'].sudo().search(...)
    ai['result'] = str(result)
except Exception as e:
    ai['result'] = f'Error: {e}'
'''
}
```

### Composer Interface Keys

| Key | UI Surface | Use Case |
|-----|------------|----------|
| `systray_ai_button` | Top bar ✨ button | Main chat with agent |
| `chatter_ai_button` | Record chatter AI button | Context-aware record help |
| `mail_composer` | Email composer AI button | Draft/reply assistance |
| `html_field_record` | HTML field AI button | Write in description fields |
| `html_field_text_select` | Selected text rewrite | Refactor/rephrase text |
| `html_prompt_shortcut` | Email prompt conversion | Convert prompt to email body |

### Prompt Button Pattern

```python
ai.prompt.button.create({
    'name': 'Summarize my inbox',
    'composer_id': composer_id,
    'sequence': 10,  # Lower = appears first
})
```

---

## Part 3: The User's Workflow & Rules

### Always Do

1. **Match existing patterns first** — look at existing agents, topics, tools before creating new ones
2. **Use MCP tools first** — only fall back to XML-RPC when MCP cannot handle the operation
3. **Document everything** — save session context, tool IDs, record IDs, decisions
4. **Follow Odoo naming conventions**: tool names = `AI: <Verb> <Noun>`
5. **Set `use_in_ai=True`** on every server action tool before linking it to a topic
6. **Verify writes** — after writing, read back to confirm the data persisted
7. **Use `sudo()`** in tool code for operations the agent needs to perform
8. **Test with real data** — create test contacts, events, emails before claiming the agent works

### Never Do

1. **NEVER expose secrets, passwords, or API keys** in responses or code
2. **NEVER commit changes** unless explicitly asked
3. **NEVER execute destructive operations** (delete/unlink) unless explicitly requested
4. **NEVER create new MCP servers** — the existing MCP server is the only one
5. **NEVER assume field names** — always check with `get_model_fields` or `fields_get`
6. **NEVER add code comments** unless the user asks for them
7. **NEVER create documentation files (README, .md files)** unless explicitly requested
8. **NEVER use emojis** unless the user uses them first

### Always Check

- `use_in_ai` field on server actions (defaults to False — must be True for AI tools)
- Correct field names (e.g. `partner_ids` not `message_partner_ids` on mail.message)
- Domain filters on many2many fields (e.g. tool_ids filters by use_in_ai=True)
- Whether a model has a `description` field before trying to write to it (ai.agent doesn't)
- Odoo version differences (Odoo 19: no `numbercall` on ir.cron)

### The User's Preferences

- Works at **AzeezTech** — Odoo consulting, AI, DevOps
- Uses **Odoo 19** (not Community vs Enterprise specific unless noted)
- Uses **OpenRouter** models (`openrouter/free` as default)
- Prefers **structured, concise responses** — no preamble, no explanation
- Values **consistency** — new components must match existing ones
- Wants **immediate action** — not planning, not speculation

---

## Part 4: Complete Agent Creation Workflow

### Step-by-Step

```
1. Research existing agents/topics/tools to understand patterns
2. Create server actions (ir.actions.server) for each tool
   - model_id=351, state='code', use_in_ai=True
   - Name: "AI: <Verb> <Noun>"
   - Code: safe_eval compatible Python
3. Create topic (ai.topic) with instructions describing all tools
4. Link tools to topic via XML-RPC (MCP can't do many2many):
   models.execute_kw(db, uid, password, 'ai.topic', 'write',
       [[topic_id], {'tool_ids': [(6, 0, [tool_id_1, ...])]}])
5. Create/update agent (ai.agent) with system prompt + topic_ids
6. Create composers (ai.composer) for desired UI surfaces
7. Create prompt buttons (ai.prompt.button) for quick actions
8. Create test data (contacts, events, emails)
9. Verify everything is configured correctly
10. Save session context to docs/
```

### System Prompt Structure

```
# {Agent Name}

## General Rules
- NEVER display errors
- ONLY use tools when needed
- If you can't complete the query, say so

## Topics
Describe each topic with its tools, triggers, and examples.

## Tools Selection
Guidance on when to use each tool category.
```

---

## Part 5: Error Diagnosis

### Silent Write Failures

**Symptom:** `execute_approved_write` returns True but data isn't saved
**Check:**
1. Domain filters on the field (e.g. `use_in_ai=True` on tool_ids)
2. Field-level security groups (e.g. `base.group_system` on tool_ids)
3. Computed/depends fields that auto-calculate
4. Overridden `write()` methods in model.py

### Invalid Field Errors

**Symptom:** `ValueError: Invalid field X.Y in condition`
**Fix:** Check actual field names with `get_model_fields` before using in domains

### MCP Many2Many Bug

**Symptom:** Many2many write returns True but relation table stays empty
**Fix:** Use XML-RPC directly instead of MCP `execute_approved_write`

### AI Agent Not Responding

**Check:**
1. Is the agent active?
2. Does it have topics with tools?
3. Are the tools linked (not just described in instructions)?
4. Does the LLM model support tool calling?
5. Is the API key configured and valid?

---

## Context

- **Domain:** Development
- **Subdomain:** MCP Integration
- **Skill ID:** skill_mcp_workflow
- **Knowledge package:** `skills/mcp_workflow/`

- **Required modules:** ai_app, mail
- **Optional modules:** calendar, discuss, social_marketing

- **Depends on skills:** skill_base, skill_ai
- **Relevant modules:** ai_app, mail, calendar, discuss

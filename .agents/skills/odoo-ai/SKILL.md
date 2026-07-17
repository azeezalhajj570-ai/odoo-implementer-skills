# Skill: odoo-ai

Odoo AI Agent Expert — Expert-level knowledge of Odoo AI agents, providers, models, tools, prompts, and sessions. Covers AI agent configuration, LLM provider integration (OpenAI, Anthropic, Azure OpenAI, Ollama, Groq), tool binding, prompt templating, security groups, usage limits, and deployment to Discuss channels, activities, and tasks. Use when the user asks about AI Agent Configuration, LLM Provider Integration, AI Model Registry, Tool Binding & Execution, Prompt Engineering in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/ai/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/ai/skill.json` — metadata, modules, dependencies
   - `skills/ai/capability.json` — detailed capability definitions
   - `skills/ai/knowledge.json` — key models, files, crons, security groups
   - `skills/ai/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **AI Agent Configuration** (`cap_ai_agent_config`): Configure ai.agent records: system prompt, welcome message, default model, provider, allowed tools, visibility, memory, and human handoff rules. Bind agents to Discuss channels, activities, and tasks.
- **LLM Provider Integration** (`cap_ai_providers`): Set up ai.provider records for OpenAI, Anthropic, Azure OpenAI, Ollama, Groq, and custom endpoints. Manage API keys, base URLs, timeout, max retries, and credential security via encrypted fields.
- **AI Model Registry** (`cap_ai_models`): Manage ai.model records: model names, context windows, token pricing, modality flags, provider links, and capability tags. Map models to providers and enforce compatibility.
- **Tool Binding & Execution** (`cap_ai_tools`): Register ai.tool records, define tool schemas, bind tools to agents, and handle tool execution loop. Includes @api decorators and JSON schema validation for function calling.
- **Prompt Engineering** (`cap_ai_prompts`): Create ai.prompt records with o_editor_prompt HTML divs, Jinja-style variables, prompt variants, and version control. Use prompt templates for content generation and agent instructions.
- **Session & Memory Management** (`cap_ai_sessions`): Manage ai.agent.session and ai_message records. Persist conversation history, summarize long threads, handle session expiry, and link sessions to Discuss channels or records.
- **AI Security & Governance** (`cap_ai_security`): Configure security groups for AI agent management, provider credential access, usage quotas, and record rules. Enforce least-privilege access to provider secrets and agent administration.
- **Agent Deployment** (`cap_ai_deployment`): Deploy agents to Discuss channels, mail activities, and project tasks. Configure auto-responders, human takeover triggers, routing rules, and channel-member visibility.
- **Usage Monitoring & Limits** (`cap_ai_monitoring`): Track token consumption, request counts, and costs per agent/provider/user. Configure usage limits, alerts, and cron-based reporting.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- AI module features depend on the installed LLM providers and available API credits
- Local models via Ollama require separate Ollama infrastructure and network access
- Provider credentials must be stored securely; plaintext secrets are not supported
- Tool execution inherits the permissions of the invoking user or bot user

## Context

- **Domain:** Platform
- **Subdomain:** AI Agents
- **Skill ID:** skill_ai
- **Knowledge package:** `skills/ai/`

- **Required modules:** ai, mail
- **Optional modules:** project

- **Depends on skills:** skill_base, skill_mail
- **Relevant modules:** ai, mail, base

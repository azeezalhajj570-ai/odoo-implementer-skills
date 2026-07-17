# OpenCode Agent Workflow Skills

This directory contains OpenCode agent workflow skills generated from the knowledge-factory skill packages in `skills/`.

## Purpose

- `skills/` holds **domain knowledge packages** (JSON metadata + prompts) consumed by the project's Python skill loader.
- `.opencode/skills/` holds **agent workflow skills** that tell OpenCode when and how to apply that domain knowledge.

Each workflow skill is a thin wrapper that points the agent at the right knowledge files and provides a consistent process for answering Odoo questions.

## Generated skills

| Skill | Source package |
|-------|----------------|
| odoo-accounting | `skills/accounting/` |
| odoo-ai | `skills/ai/` |
| odoo-base | `skills/base/` |
| odoo-crm | `skills/crm/` |
| odoo-development | `skills/development/` |
| odoo-ecommerce | `skills/ecommerce/` |
| odoo-hr | `skills/hr/` |
| odoo-inventory | `skills/inventory/` |
| odoo-mail | `skills/mail/` |
| odoo-manufacturing | `skills/manufacturing/` |
| odoo-marketing | `skills/marketing/` |
| odoo-migration | `skills/migration/` |
| odoo-platform-recovery | `skills/platform_recovery/` |
| odoo-project | `skills/project/` |
| odoo-purchase | `skills/purchase/` |
| odoo-security | `skills/security/` |
| odoo-social-marketing | `skills/social_marketing/` |
| odoo-technical-due-diligence | `skills/technical_due_diligence/` |
| odoo-website | `skills/website/` |

## Regenerating

After editing a knowledge package, regenerate the workflow skills:

```bash
python3 scripts/generate_agent_skills.py
```

## Manual overrides

If a workflow skill needs richer process steps than the generator can produce, edit the generated `SKILL.md` directly. To preserve manual edits, add a `manual: true` guard to the generator or keep the manual file separate.

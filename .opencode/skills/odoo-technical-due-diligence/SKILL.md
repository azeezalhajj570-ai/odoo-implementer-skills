---
name: odoo-technical-due-diligence
description: Use when the user asks about AI Platform Technical Due Diligence topics such as Architecture Review, AI Design Review, Odoo Implementation Review in Odoo 19. Loads knowledge from skills/technical_due_diligence/.
---

# Skill: odoo-technical-due-diligence

AI Platform Technical Due Diligence — Performs independent, skeptical, engineering-grade technical due diligence reviews of AI platforms, autonomous agent systems, and Odoo-related architectures. Evaluates architecture soundness, AI design, Odoo expertise, scalability, security, production readiness, and commercial viability. Use when the user asks about Architecture Review, AI Design Review, Odoo Implementation Review, Scalability Review, Security Review in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/technical_due_diligence/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/technical_due_diligence/skill.json` — metadata, modules, dependencies
   - `skills/technical_due_diligence/capability.json` — detailed capability definitions
   - `skills/technical_due_diligence/knowledge.json` — key models, files, crons, security groups
   - `skills/technical_due_diligence/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Architecture Review** (`cap_architecture_review`): Evaluate separation of concerns, component independence, over-engineering, under-engineering, and architectural debt across platform layers.
- **AI Design Review** (`cap_ai_design_review`): Distinguish real AI/ML systems from keyword matchers and template lookups. Evaluate reasoning, planning, memory, self-correction, and multi-agent coordination.
- **Odoo Implementation Review** (`cap_odoo_review`): Assess whether a platform can actually implement, maintain, migrate, and operate Odoo Enterprise, Community, OCA, and custom modules.
- **Scalability Review** (`cap_scalability_review`): Identify bottlenecks under enterprise-scale assumptions: thousands of modules, hundreds of databases, billions of rows, distributed teams, multi-cloud.
- **Security Review** (`cap_security_review`): Evaluate prompt injection, tool abuse, MCP security, secrets management, credential handling, supply chain, plugin, and autonomous execution risks.
- **Production Readiness Assessment** (`cap_production_readiness`): Check observability, tracing, audit logs, rollback, versioning, disaster recovery, HA, backups, multi-tenancy, rate limiting, approvals, policy, and compliance.
- **Competitive Analysis** (`cap_competitive_review`): Compare platform capabilities against GitHub Copilot, Cursor, Claude Code, OpenHands, Devin, Odoo Studio, Odoo Upgrade Service, and similar tools.
- **Technical Debt Assessment** (`cap_technical_debt`): Estimate architecture debt, maintenance cost, learning curve, operational cost, complexity, documentation burden, testing burden, and future scalability.
- **Commercial Evaluation** (`cap_commercial_evaluation`): Assess market fit, differentiation, competitive advantage, business value, risk level, time to production, team size, and development time.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Requires access to source code, architecture docs, and test results for accurate review
- Scores are qualitative and should be calibrated against investor/enterprise criteria
- Does not perform automated penetration testing or performance benchmarking

## Context

- **Domain:** Platform
- **Subdomain:** Technical Due Diligence
- **Skill ID:** skill_tdd
- **Knowledge package:** `skills/technical_due_diligence/`


- **Depends on skills:** skill_base

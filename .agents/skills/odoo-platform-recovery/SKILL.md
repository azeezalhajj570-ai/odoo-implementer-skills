# Skill: odoo-platform-recovery

Platform Recovery and Salvage Planner — Helps teams recover from under-implemented AI platforms by identifying valuable components, merging or deleting stubs, and producing phased rebuild roadmaps with real technology choices. Use when the user asks about Valuable Component Extraction, Component Consolidation, Production Foundation Design, AI Layer Redesign, Digital Twin Redesign in Odoo 19.

## Domain anchors

- Reference exact model and field names when answering technical questions.
- Distinguish Community vs Enterprise features explicitly.
- Align guidance with the project knowledge base in `skills/platform_recovery/`.
- Prefer Odoo 19 patterns and syntax; call out version differences when relevant.

## Process

1. **Clarify the task**  
   Determine if the user needs configuration, code, debugging, migration, review, or explanation. Ask one clarifying question if the scope is ambiguous.

2. **Load domain knowledge**  
   Read the relevant files for this skill:
   - `skills/platform_recovery/skill.json` — metadata, modules, dependencies
   - `skills/platform_recovery/capability.json` — detailed capability definitions
   - `skills/platform_recovery/knowledge.json` — key models, files, crons, security groups
   - `skills/platform_recovery/prompt.md` — the system prompt for this domain

3. **Select the right capability**  
   Match the user's request to one of the domain capabilities:

- **Valuable Component Extraction** (`cap_value_extraction`): Identify which parts of a stub codebase are worth keeping and which should be discarded.
- **Component Consolidation** (`cap_component_consolidation`): Recommend merging redundant engines and deleting unnecessary components.
- **Production Foundation Design** (`cap_foundation_design`): Design real backend, auth, multi-tenancy, connectors, and storage architecture.
- **AI Layer Redesign** (`cap_ai_redesign`): Replace keyword/template engines with LLMs, RAG, embeddings, and existing agent frameworks.
- **Digital Twin Redesign** (`cap_twin_redesign`): Replace dictionary-based twins with event-driven graph models, delta history, and conflict resolution.
- **Real Connector Design** (`cap_connector_design`): Design secure, least-privilege connectors for PostgreSQL, Odoo ORM, Git, Docker, and Kubernetes.
- **Phased Rebuild Roadmap** (`cap_rebuild_roadmap`): Produce a time-boxed, team-sized, milestone-driven plan to rebuild the platform.
- **Scope Reduction Strategy** (`cap_scope_reduction`): Identify the smallest valuable use case to ship first instead of rebuilding all layers.

4. **Produce output**  
   Return one of: configuration steps, Python/XML code, migration notes, or a concise explanation. Include required modules and any limitations.

5. **Verify**  
   Cross-check the answer against the limitations and supported modules below.

## Limitations

- Requires an existing due diligence review or detailed project knowledge
- Cannot automatically execute the recovery plan
- Recommendations assume access to a qualified engineering team

## Context

- **Domain:** Platform
- **Subdomain:** Platform Recovery
- **Skill ID:** skill_platform_recovery
- **Knowledge package:** `skills/platform_recovery/`


- **Depends on skills:** skill_base, skill_tdd

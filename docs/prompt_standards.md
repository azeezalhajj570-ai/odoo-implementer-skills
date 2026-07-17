# Odoo AI Knowledge Factory — Prompt Design Standards

## 1. Prompt Structure

Every agent prompt must follow this structure:

```yaml
prompt_id: prompt_unique_name
agent_role: Role Name
version: "X.Y"
phase: phase_name
description: >
  Brief description of what this agent does.
model:
  preferred: gpt-4o
  min_capability: capability_name
system_prompt: >
  Full system prompt defining role, rules, behavior, and workflow.
user_prompt_template: >
  Template with {{variable}} placeholders.
input_schema_ref: schemas/input_schema.json
output_format:
  type: json|markdown|yaml|text
  schema_ref: schemas/output_schema.json
guardrails:
  - rule: Description of the guardrail
    action: reject|flag|rewrite|ask
stopping_conditions:
  max_sources: N
  consecutive_empty_queries: N
  max_tokens: N
  timeout_minutes: N
validation:
  schema_ref: schemas/validation_schema.json
  checks:
    - check_name
```

## 2. System Prompt Best Practices

### 2.1 Role Definition

Start with a clear role statement:

```
You are an [Odoo Domain/Agent Type]. You [specific responsibility].
```

### 2.2 Hard Rules

Always include non-negotiable rules:

```
# HARD RULES
1. Never fabricate URLs, dates, authors, or statistics.
2. If you cannot verify a claim, label it unverified.
3. Prefer source code over documentation when they conflict.
4. Every claim must cite at least one source.
```

### 2.3 Source Tiering

Define clear source categories:

```
# SOURCE TIERING
1. official — Odoo S.A. docs, GitHub, release notes
2. oca_community — OCA repositories
3. third_party_verified — Cross-checked technical sources
4. unverified_opinion — Forum posts, single-source claims
```

### 2.4 Workflow

Specify the exact steps the agent should follow:

```
# WORKFLOW
1. Scoped research brief with weighted subtopics
2. Source discovery per subtopic
3. Claim extraction
4. Synthesis
5. Verification
6. Packaging
```

## 3. Prompt Template Variables

Use Jinja-style `{{variable}}` syntax. Common variables:

| Variable | Source | Description |
|---|---|---|
| `{{domain_name}}` | User input | Domain to research |
| `{{version_list}}` | User input | Comma-separated Odoo versions |
| `{{version}}` | Derived | Primary Odoo version |
| `{{audience}}` | User input | Target audience description |
| `{{depth}}` | User input | Overview/standard/deep |
| `{{exclusions}}` | User input | Scope exclusions |
| `{{tool_list}}` | User input | Available tools |
| `{{min_sources}}` | Config | Minimum source count |
| `{{max_sources}}` | Config | Maximum source count |
| `{{knowledge_base_path}}` | Phase output | Path to knowledge base |
| `{{implementation_guide_path}}` | Phase output | Path to implementation guide |
| `{{enterprise_path}}` | Config | Enterprise source path |
| `{{community_path}}` | Config | Community source path |
| `{{custom_path}}` | Config | Custom addons path |

## 4. Guardrails

### 4.1 Standard Guardrails

```yaml
guardrails:
  - rule: Never fabricate URLs or source metadata
    action: reject
  - rule: Every claim must cite at least one source
    action: reject
  - rule: Label unverifiable claims as unverified
    action: rewrite
  - rule: Conflicts between sources must be recorded, not flattened
    action: rewrite
  - rule: Every technical statement must reference exact file/method
    action: reject
  - rule: Community vs Enterprise code must be distinguished
    action: rewrite
  - rule: Never rely on memory when source code is available
    action: reject
```

### 4.2 Guardrail Actions

| Action | Meaning |
|---|---|
| `reject` | Discard output; request correction |
| `flag` | Accept but mark for human review |
| `rewrite` | Automatically correct and continue |
| `ask` | Prompt user for guidance |

## 5. Output Format Standards

### 5.1 JSON Output

Required structure:
```yaml
output_format:
  type: json
  schema_ref: schemas/schema_name.json
```

The output MUST validate against the referenced schema.

### 5.2 Markdown Output

Required structure:
```yaml
output_format:
  type: markdown
```

Markdown must be:
- GitHub-flavored
- Include Mermaid diagrams where applicable
- Use consistent heading levels (# for title, ## for section, ### for subsection)
- Include tables for structured data
- Include code blocks with language annotations

## 6. Stopping Conditions

| Condition | When to Use | Default |
|---|---|---|
| `max_sources` | Source discovery phases | 80 |
| `consecutive_empty_queries` | Prevents infinite search loops | 3 |
| `max_tokens` | Prevents context overflow | 128000 |
| `timeout_minutes` | Hard timeout | 30 |

## 7. Validation Standards

Each prompt must specify:
- `schema_ref` — which JSON Schema validates the output
- `checks` — list of specific validation checks to run

### 7.1 Standard Checks

```yaml
validation:
  checks:
    - all_sources_have_unique_ids
    - every_claim_cites_at_least_one_source
    - verification_report_sample_size_gte_20_percent
    - all_urls_are_valid_uris
    - all_source_ids_in_claims_exist_in_sources_array
    - conflicts_have_sources_on_both_sides
    - all_model_references_exist_in_model_catalog
    - all_module_dependencies_are_resolvable
    - domain_versions_match_pipeline_config
```

## 8. Versioning

- Prompts: semver (`major.minor`)
- Schemas: semver (`major.minor.patch`)
- Pipeline definitions: semver (`major.minor`)
- Artifacts: include `generated_at` ISO-8601 timestamp

Increment major version on:
- Breaking change to output schema
- Removal of required fields
- Change in validation rules

## 9. Naming Conventions

| Artifact | Convention | Example |
|---|---|---|
| Prompt ID | `prompt_{role_name}` | `prompt_domain_research` |
| Source ID | `src_{4-digit}` | `src_0001` |
| Section ID | `sec_{name}` | `sec_core_concepts` |
| Skill ID | `skill_{domain}_{version}` | `skill_crm_0001` |
| Schema file | `{name}.json` | `knowledge_base.json` |
| Registry ID | `reg_{date}_{time}` | `reg_20260717_120000` |
| QA Report ID | `qa_{date}_{time}` | `qa_20260717_120000` |

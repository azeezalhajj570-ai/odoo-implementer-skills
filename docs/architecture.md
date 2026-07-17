# Odoo AI Knowledge Factory — Architecture Guide

## 1. System Architecture

The Knowledge Factory is a modular, pipeline-based framework that transforms Odoo domain knowledge into structured, verifiable, AI-ready artifacts.

### 1.1 High-Level Data Flow

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Official  │   │ Source   │   │ Source   │   │ Domain   │
│ Docs      │──▶│ Discovery│──▶│ Verified │──▶│ Research │
└──────────┘   └──────────┘   └──────────┘   └─────┬────┘
┌──────────┐                                        │
│ GitHub   │──▶ Source Code Analysis ───────────────┤
│ Repos    │                                        │
└──────────┘                                        │
┌──────────┐                                        │
│ OCA      │──▶ Business Process Extraction ────────┤
│ Modules  │                                        │
└──────────┘                                        │
┌──────────┐                                        │
│ AI       │──▶ AI Integration Analysis ────────────┤
│ Platform │                                        │
└──────────┘                                        │
                                                   ▼
                                            ┌──────────┐
                                            │   AI     │
                                            │  Skills  │
                                            └────┬─────┘
                                                 │
                                            ┌────▼─────┐
                                            │ Knowledge │
                                            │ Package   │
                                            └────┬─────┘
                                                 │
                                            ┌────▼─────┐
                                            │    QA    │
                                            │ Validate │
                                            └──────────┘
```

### 1.2 Component Architecture

#### Agent Layer
Each agent is an AI system (LLM + tools) configured by a prompt definition:
- **System Prompt** — Role definition, hard rules, behavior constraints
- **User Prompt Template** — Parameterized input with Jinja-style variables
- **Input Schema** — References a JSON Schema for input validation
- **Output Schema** — References a JSON Schema for output validation
- **Guardrails** — Rules for rejecting/flagging/rewriting outputs
- **Stopping Conditions** — When to stop searching/processing

#### Schema Layer
All data structures are defined by JSON Schemas (draft-07):
- Ensure structural consistency across all domains
- Enable automated validation
- Support cross-artifact reference integrity
- Define the canonical format for RAG indexing

#### Pipeline Layer
Workflows (YAML) define phase execution order, dependencies, and data flow:
- `pipeline.yaml` — Full 7-phase pipeline
- `single_skill.yaml` — Single skill generation from existing artifacts
- `qa_pipeline.yaml` — Standalone QA validation

#### Storage Layer
- `output/databases/` — Machine-readable JSON artifacts
- `output/reports/` — Human-readable Markdown documentation
- `skills/{domain}/` — Generated AI Skills
- `domains/references/` — Cross-domain reference materials

## 2. Phase Detail

### 2.1 Phase 1: Domain Research

**Purpose:** Build a verified, citable knowledge base for a domain.

**Inputs:**
- Domain name, Odoo versions, audience, depth level
- Excluded scope, available tools, source budget

**Agents:**
- `domain_research_agent` — Orchestrates the full research pipeline
- `source_discovery_agent` — Searches and fetches per subtopic
- `source_verification_agent` — Re-checks 20%+ sample of sources

**Outputs:**
- `knowledge_base.json` — Canonical knowledge with claims, sources, conflicts, gaps
- `knowledge_base.md` — Human-readable derived documentation

**Validation:**
- Every claim must cite ≥1 source
- Source verification sample ≥20%
- Conflicts recorded, not flattened
- Known gaps explicitly stated

### 2.2 Phase 2: Source Code Intelligence

**Purpose:** Analyze actual Odoo source code for implementation intelligence.

**Inputs:**
- Domain knowledge base (for context)
- Enterprise, Community, Custom source paths

**Agent:**
- `source_code_analysis_agent` — Reads manifests, models, views, security, controllers, wizards, tests

**Outputs:**
- `module_catalog.json` — Modules with versions, deps, models, crons, controllers, ACLs
- `model_catalog.json` — Models with inheritance, fields, methods, constraints, computed fields

**Validation:**
- Every technical statement must reference exact file/method
- Community vs Enterprise code must be distinguished
- Conflicts with documentation must be recorded

### 2.3 Phase 3: Business Intelligence

**Purpose:** Extract business processes and implementation patterns.

**Inputs:**
- Knowledge base + module/model catalog + implementation guide

**Agent:**
- `business_process_agent` — Extracts workflows, patterns, best practices

**Outputs:**
- `business_processes.md` — Documented business processes with code patterns

### 2.4 Phase 4: AI Integration

**Purpose:** Identify AI enhancement opportunities.

**Inputs:**
- Knowledge base + implementation guide

**Agent:**
- `ai_integration_agent` — Maps AI capabilities to domain features

**Outputs:**
- `ai_opportunities.json` — AI integration opportunities with implementation details

### 2.5 Phase 5: AI Skill Generation

**Purpose:** Generate production-ready AI Skills.

**Inputs:**
- Knowledge base + implementation guide + AI opportunities

**Agent:**
- `skill_generator_agent` — Generates skill definitions

**Outputs:**
- `skills/{domain}/*.json` — AI Skill definitions

### 2.6 Phase 6: Knowledge Packaging

**Purpose:** Package all artifacts for consumption.

**Agents:**
- `documentation_generator` — Derives Markdown from JSON
- `json_generator` — Validates and normalizes JSON
- `knowledge_graph_generator` — Generates Mermaid diagrams + node/edge lists
- `rag_packaging_agent` — Chunks, indexes, and generates metadata

### 2.7 Phase 7: Quality Assurance

**Purpose:** Validate all artifacts for integrity.

**Agent:**
- `qa_agent` — Runs 11 categories of checks

**Check Categories:**
1. Broken references
2. Missing citations
3. Duplicate content (cosine similarity ≥0.85)
4. Contradictions
5. Hallucination risk
6. Unsupported claims
7. Missing metadata
8. Invalid JSON
9. Schema validation
10. Cross-reference integrity
11. Stale data

## 3. Data Flow Between Phases

```
Phase 1 ──▶ knowledge_base.json ──▶ Phase 2 (context)
                                   ──▶ Phase 3 (input)
                                   ──▶ Phase 4 (input)
                                   ──▶ Phase 5 (input)

Phase 2 ──▶ module_catalog.json ──▶ Phase 3 (input)
           model_catalog.json    ──▶ Phase 4 (input)
           implementation.md     ──▶ Phase 5 (input)

Phase 3 ──▶ business_processes.md ──▶ Phase 6 (packaging)

Phase 4 ──▶ ai_opportunities.json ──▶ Phase 5 (input)

Phase 5 ──▶ skills/*.json ──▶ Phase 6 (packaging)

Phase 6 ──▶ complete.json, complete.md, graph.md, rag_metadata.json

Phase 7 ──▶ qa_report.json, qa_summary.md
```

## 4. Schema Relationships

```
knowledge_base.json
    ├── sources[] → source_registry.json#entries[]
    ├── sections[].claims[].source_ids → sources[].id
    └── verification_report → (inline)

module_catalog.json
    ├── modules[].depends → modules[].technical_name (self-reference)
    └── dependency_graph.edges[][] → modules[].technical_name

model_catalog.json
    └── models[].fields[].relation → models[].name (self-reference)

skill_definition.json
    ├── required_knowledge[].source_ids → sources[].id
    └── related_skills → skill_definition[].skill_id (self-reference)

metadata.json
    └── cross_references[].target_id → any artifact ID

validation_report.json
    └── checks[].location → artifact path + section
```

## 5. Extension Guide

### Adding a New Domain

1. **Create domain entry** (optional):
```bash
mkdir -p domains/{domain_name}
```

2. **Run pipeline**:
```bash
python3 scripts/orchestrator.py \
    --domain "My Domain" \
    --versions "19.0" \
    --depth deep
```

3. **Review QA report** at `output/reports/{domain}_qa_report.json`

### Adding a New Agent

1. **Create prompt file** in `prompts/{agent_name}/`:
```yaml
prompt_id: prompt_custom_agent
agent_role: Custom Agent Role
version: "1.0"
phase: custom_phase
system_prompt: "..."
user_prompt_template: "..."
input_schema_ref: "schemas/input_schema.json"
output_format:
  type: json
  schema_ref: "schemas/output_schema.json"
```

2. **Add to pipeline** in `workflows/pipeline.yaml`

### Adding a New Schema

1. **Create schema** in `schemas/`
2. **Register validator** in `scripts/qa_validator.py`:
```python
@register_validator("my_schema")
def validate_my_schema(v, data, path):
    ...
```

### Customizing Prompts

- Edit prompt YAML files directly for agent behavior changes
- Update `user_prompt_template` with new variables
- Modify `system_prompt` for role/rule changes
- Update `guardrails` for new constraints

# Odoo AI Knowledge Factory

A multi-layered AI skill platform for Odoo. It packages expert-level Odoo domain knowledge into portable, machine-readable AI Skills that can be loaded by agents to implement, configure, consult on, and operate Odoo systems.

> **Status:** Functional skill platform. The skill loading, registry, validation engine, knowledge graph, RAG builder, and 19 domain skills are implemented. Higher-layer autonomous engines (Reasoning, Execution, OAIOS, etc.) are archived as design work in `archive/design/` and are not production-ready.

---

## Architecture

The platform is organized into six conceptual layers. Layers 1–2 and the Validation Engine are implemented. Layers 3–6 exist as design artifacts in `archive/design/`.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 6 — Enterprise Intelligence Platform (design archive)  │
├─────────────────────────────────────────────────────────────┤
│ Layer 5 — Odoo AI Operating System (design archive)          │
├─────────────────────────────────────────────────────────────┤
│ Layer 4 — Autonomous Odoo AI Consultant (design archive)     │
├─────────────────────────────────────────────────────────────┤
│ Layer 3 — Autonomous Odoo Implementer (partial)             │
│   Validation Engine is implemented; Execution is archived    │
├─────────────────────────────────────────────────────────────┤
│ Layer 2 — OpenCode AI Skill Platform (implemented)           │
│   Skill Loader, Registry, Dependency Manager, Knowledge     │
│   Graph, RAG Builder                                         │
├─────────────────────────────────────────────────────────────┤
│ Layer 1 — Knowledge Factory (implemented)                    │
│   Schemas, Prompts, Workflows, Orchestrator, QA Validator   │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Run the test suite

```bash
./tests/run_all.sh
```

### Discover and load skills

```python
from agents.opencode.skill_loader import SkillLoader

loader = SkillLoader()
loader.discover()
skill = loader.load("skill_crm")
print(skill.name)
print(skill.get_capabilities())
```

### Create a skill session

```python
from agents.opencode.adapter import OpenCodeAdapter

adapter = OpenCodeAdapter()
adapter.initialize()
session = adapter.create_session(
    agent_type="developer",
    required_capabilities=["cap_pipeline", "cap_lead_scoring"]
)
print(session.get_prompts())
```

### Validate an Odoo module

```python
from execution.validator import ValidationEngine

validator = ValidationEngine()
results = validator.validate_module("/path/to/odoo/module")
print(results)
```

### Run the pipeline prompt builder

```bash
python3 scripts/orchestrator.py \
    --domain "CRM" \
    --versions "19.0" \
    --depth deep
```

> Note: `orchestrator.py` builds prompt strings from YAML templates. It does not execute AI agents or the skill platform.

---

## Repository Structure

```
knowledge-factory/
├── agents/opencode/            # Working skill platform
│   ├── skill_loader.py         # Skill discovery and loading
│   ├── skill_registry.py       # Skill indexing
│   ├── dependency_manager.py   # Dependency resolution
│   ├── adapter.py              # OpenCode agent adapter
│   └── update_manager.py       # Skill staleness detection
├── archive/design/             # Archived design work
│   ├── coordinator/            # Multi-Agent Coordinator stub
│   ├── execution_engine.py     # Execution Engine stub
│   ├── memory/                 # Memory and Self-Correction stubs
│   ├── oaios/                  # OAIOS data models and templates
│   ├── project/                # Project Context Engine stub
│   ├── reasoning/              # Reasoning/Planning/Decision stubs
│   ├── reports/                # Report Generator stub
│   ├── workflow_runner.py      # Workflow Runner stub
│   └── tests/                  # Tests for archived components
├── archive/skill-tools/        # Skill tool scripts (not wired in)
├── archive/skill-workflows/    # Skill workflow files (not wired in)
├── docs/                       # Framework documentation
├── execution/                  # ValidationEngine only
│   └── validator.py            # Python/XML/manifest/ACL validation
├── graphs/                     # Knowledge Graph Engine
├── output/
│   └── skill_registry.json     # Compiled skill registry
├── prompts/                    # 12 agent prompt YAMLs
├── rag/                        # RAG Builder
│   └── builder.py
├── schemas/                    # JSON schemas for all artifacts
├── scripts/                    # Standalone utilities
│   ├── orchestrator.py         # Prompt builder
│   └── qa_validator.py         # JSON validation tool
├── skills/                     # 19 AI Skill packages
├── templates/
│   └── knowledge_base/         # Knowledge base template
├── tests/                      # Active test suite
├── tools/                      # Tool Registry and MCP Adapter
└── README.md
```

---

## AI Skills

The platform currently contains **19 skills** across **11 domains** with **159 capabilities**:

| Skill | Domain | Description |
|-------|--------|-------------|
| `skill_accounting` | Finance | Odoo Accounting |
| `skill_ai` | Platform | Odoo AI Agent module |
| `skill_base` | Platform | Odoo Platform Foundation |
| `skill_crm` | Sales | Odoo CRM |
| `skill_development` | Development | Odoo Development |
| `skill_ecommerce` | Website | Odoo eCommerce |
| `skill_hr` | Human Resources | Odoo HR |
| `skill_inventory` | Operations | Odoo Inventory |
| `skill_mail` | Platform | Odoo Mail & Communication |
| `skill_manufacturing` | Operations | Odoo Manufacturing |
| `skill_marketing` | Marketing | Odoo Marketing Automation |
| `skill_migration` | Migration | Odoo Migration |
| `skill_platform_recovery` | Platform | Platform Recovery & Salvage Planner |
| `skill_project` | Project | Odoo Project Management |
| `skill_purchase` | Operations | Odoo Purchase |
| `skill_security` | Security | Odoo Security |
| `skill_social_marketing` | Marketing | Odoo Social Marketing |
| `skill_tdd` | Platform | AI Platform Technical Due Diligence |
| `skill_website` | Website | Odoo Website |

Each active skill package contains:
- `skill.json` — metadata, dependencies, capabilities, schemas
- `capability.json` — detailed capability definitions
- `knowledge.json` — key models, files, crons, security groups, record rules
- `prompt.md` — system prompt for the domain expert
- `evaluation/functional.json` — functional Q&A
- `evaluation/technical.json` — technical Q&A

Archived skill artifacts (tools, workflows, analyzers, etc.) are preserved in `archive/skill-tools/` and `archive/skill-workflows/` but are not loaded by the skill platform.

The skill registry is compiled to `output/skill_registry.json`.

---

## Tests

Run the active test suite:

```bash
./tests/run_all.sh
```

Individual test files:

```bash
python3 tests/test_schema_validity.py
python3 tests/test_qa_validator.py
python3 tests/test_orchestrator.py
python3 tests/test_platform_integration.py
```

Archived tests for stub components:

```bash
python3 archive/design/tests/test_consulting_layer.py
python3 archive/design/tests/test_execution_platform.py
python3 archive/design/tests/test_oaios_layer5.py
```

---

## What Is Implemented

### Working components
- **Skill loading and registry** — discover, load, cache, dependency resolution
- **Knowledge graph** — directed graph with BFS, shortest path, community detection
- **Validation engine** — Python syntax, XML parsing, Odoo manifest, ACL CSV validation
- **RAG builder** — text chunking and metadata generation
- **Skill packages** — 19 domain skills with prompts, knowledge, and evaluations
- **Upgrade reference data** — 18→19 breaking changes and deprecated APIs
- **Standalone utilities** — orchestrator prompt builder, QA validator

### Archived design work
- Reasoning, planning, decision, memory, self-correction
- Digital Twin, connectors, health engine, simulation, observer, optimizer, incident response, dashboard
- Execution engine, workflow runner, multi-agent coordinator
- Project context engine, report generator, plugin manager

See `archive/design/README.md` for details.

---

## Design Principles

- **Modular** — Components are separated by layer and responsibility
- **Skill-centric** — Domain knowledge is packaged into portable AI skills
- **Source-driven** — Skills cite Odoo models, files, and version specifics
- **Schema-validated** — Skill metadata conforms to JSON schemas
- **Tested** — Active components are covered by tests
- **Extensible** — New domains can be added as new skill directories
- **Honest** — Stubs and design work are archived, not presented as production code

---

## License

This framework is designed for use with Odoo Enterprise under the applicable Odoo Enterprise License. Component licenses vary (LGPL-3 for community code, OEEL-1 for Enterprise code, OPL-1 for proprietary modules).

---

## Disclaimer

The higher-layer autonomous systems are archived design work and should not be used to execute real changes on production Odoo systems. Only the Validation Engine and skill platform are suitable for real use, and even those should be integrated into a proper production backend before handling customer data.

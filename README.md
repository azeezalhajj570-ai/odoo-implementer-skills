# Odoo AI Knowledge Factory

A multi-layered AI skill platform for Odoo. It packages expert-level Odoo domain knowledge into portable, machine-readable AI Skills that can be loaded by agents to implement, configure, consult on, and operate Odoo systems.

> **Status:** Functional skill platform. The skill loading, registry, knowledge graph, validation engine, and 19 domain skills are implemented. The higher-layer autonomous engines (Reasoning, Execution, Digital Twin, etc.) are architectural stubs that return template-based results and are not production-ready.

---

## Architecture

The platform is organized into six layers. Layers 1–2 and the Validation Engine are implemented. Layers 3–6 exist as code structure and data models but most components are not backed by real AI models or runtime integrations.

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 6 — Enterprise Intelligence Platform (planned)         │
│   Enterprise Registry, Portfolio Digital Twin, Fleet Planner│
├─────────────────────────────────────────────────────────────┤
│ Layer 5 — Odoo AI Operating System (OAIOS)                  │
│   Digital Twin, Connectors, Health Engine, Simulation,      │
│   Observer, Optimizer, Incident Response, Dashboard           │
│   (implemented as data models and templates)                 │
├─────────────────────────────────────────────────────────────┤
│ Layer 4 — Autonomous Odoo AI Consultant                       │
│   Reasoning Engine, Planner, Decision Engine, Multi-Agent   │
│   Coordinator, Memory, Self-Correction, Report Generator      │
│   (keyword/template-based, not real AI)                      │
├─────────────────────────────────────────────────────────────┤
│ Layer 3 — Autonomous Odoo Implementer                       │
│   Execution Engine, Workflow Runner, Validation Engine,       │
│   Project Context Engine, Tool Registry, MCP Adapter          │
│   (Validation Engine is real; execution is a stub)            │
├─────────────────────────────────────────────────────────────┤
│ Layer 2 — OpenCode AI Skill Platform                          │
│   Skill Loader, Skill Registry, Dependency Manager,           │
│   Knowledge Graph, RAG Builder, Plugin System               │
│   (fully implemented)                                         │
├─────────────────────────────────────────────────────────────┤
│ Layer 1 — Knowledge Factory                                   │
│   Schemas, Prompts, Workflows, Orchestrator, QA Validator   │
│   (pipeline builds prompts; does not execute real AI)         │
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

### Run the pipeline (prompt builder only)

```bash
python3 scripts/orchestrator.py \
    --domain "CRM" \
    --versions "19.0" \
    --depth deep
```

---

## Repository Structure

```
knowledge-factory/
├── agents/                     # OpenCode agent integration
│   └── opencode/               # SkillLoader, SkillRegistry, DependencyManager, Adapter
├── coordinator/                # Multi-Agent Coordinator (stub)
├── docs/                         # Architecture, extension, and prompt standards
├── domains/                      # Domain reference placeholders
├── examples/                     # Example output placeholders
├── execution/                    # Execution Engine, Workflow Runner, Validation Engine
├── graphs/                       # Knowledge Graph Engine
├── memory/                       # Experience Memory, Self-Correction (stub)
├── oaios/                        # Odoo AI Operating System (data models)
│   ├── connectors/               # Connector Registry (stub)
│   ├── dashboard/                # Executive Dashboard (stub)
│   ├── health/                   # Health Engine (stub)
│   ├── incident/                 # Incident Response Engine (stub)
│   ├── observer/                 # Business Process Observer (stub)
│   ├── optimizer/                # Optimization Engine (stub)
│   ├── scanner/                  # Live Scanner (file change detector)
│   ├── simulation/               # Simulation Engine (stub)
│   ├── twin/                     # Digital Twin (data model)
│   └── upgrade/                  # Upgrade Simulation Engine (reference data)
├── plugins/                      # Plugin Manager
├── project/                      # Project Context Engine, Monitor
├── prompts/                      # 12 agent prompt YAMLs
├── rag/                          # RAG Builder
├── reasoning/                    # Reasoning, Planner, Decision Engine (stub)
├── reports/                      # Report Generator
├── schemas/                      # JSON schemas for all artifacts
├── scripts/                      # Orchestrator and QA Validator
├── skills/                       # AI Skill packages (19 skills)
├── templates/                    # Output templates
├── tests/                        # Test suite (7 test files)
├── tools/                        # Tool Registry and MCP Adapter
└── workflows/                    # Pipeline orchestration YAMLs
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

Each skill package contains:
- `skill.json` — metadata, dependencies, capabilities, schemas
- `capability.json` — detailed capability definitions
- `knowledge.json` — key models, files, crons, security groups, record rules
- `prompt.md` — system prompt for the domain expert
- `evaluation/functional.json` — functional Q&A
- `evaluation/technical.json` — technical Q&A
- `tools/*.py` — small analyzer/validator scripts
- `workflows/*.json` — implementation workflows

The skill registry is compiled to `output/skill_registry.json`.

---

## Tests

Run the test suite:

```bash
./tests/run_all.sh
```

Individual test files:

```bash
python3 tests/test_schema_validity.py
python3 tests/test_qa_validator.py
python3 tests/test_orchestrator.py
python3 tests/test_platform_integration.py
python3 tests/test_execution_platform.py
python3 tests/test_consulting_layer.py
python3 tests/test_oaios_layer5.py
```

---

## What Is Implemented vs. Stub

### Implemented and functional
- **Skill loading and registry** — discover, load, cache, dependency resolution
- **Knowledge graph** — directed graph with BFS, shortest path, community detection
- **Validation engine** — Python syntax, XML parsing, Odoo manifest, ACL CSV validation
- **Skill packages** — 19 domain skills with prompts, knowledge, evaluations, tools, workflows
- **RAG builder** — text chunking and metadata generation
- **Upgrade reference data** — 18→19 breaking changes and deprecated APIs

### Implemented as structure / templates
- Reasoning, planning, decision, memory, self-correction
- Digital Twin, connectors, health engine, simulation, observer, optimizer, incident response, dashboard
- Execution engine, workflow runner, multi-agent coordinator
- These return hardcoded or template-based results and are not connected to real systems or AI models.

### Not implemented
- Real LLM integration
- Real database connectors (PostgreSQL, Odoo ORM, Git, Docker, Kubernetes)
- Authentication, authorization, audit logging, multi-tenancy
- Production observability, HA, backups, rollback
- Enterprise Intelligence Platform (Layer 6)

---

## Design Principles

- **Modular** — Components are separated by layer and responsibility
- **Skill-centric** — Domain knowledge is packaged into portable AI skills
- **Source-driven** — Skills cite Odoo models, files, and version specifics
- **Schema-validated** — Skill metadata conforms to JSON schemas
- **Tested** — All skill packages and schemas are covered by tests
- **Extensible** — New domains can be added as new skill directories

---

## License

This framework is designed for use with Odoo Enterprise under the applicable Odoo Enterprise License. Component licenses vary (LGPL-3 for community code, OEEL-1 for Enterprise code, OPL-1 for proprietary modules).

---

## Disclaimer

This is a research and skill-packaging platform. The higher-layer autonomous systems (Layer 3–5) are architectural stubs and should not be used to execute real changes on production Odoo systems without significant further development.
